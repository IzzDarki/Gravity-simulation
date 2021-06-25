import pygame
import imgui
import math
import random
from datetime import datetime

from utility import *
from body import Body

class App:
	GRAVITATIONAL_CONSTANT = 6.67384e-20 # for calculating force in kg * km / s^2
	ZOOM_STEP = 1.1

	def __init__(self):
		self.running = True
		self.last_micros = 0
		
		self.window_width = 1080 # size of the window
		self.window_height = 720
		self.view_width = 350_000_000 # size of the model
		self.view_start_x = -self.view_width / 2 # x-position (in the model) at the left edge of the window
		self.view_start_y = self.view_start_x * self.window_height / self.window_width
		self.fixed_body: Body = None # if this is a body, then the view always changes, so that the body is in a fixed place

		self.generate_background_stars()

		# model
		sun = Body(
			name = "sun",
			mass = 1.989e30,
			pos_x = 0, pos_y = 0,
			velocity_x = 0, velocity_y = 0,
			pos_to_screen_pos = self.pos_to_screen_pos,
			color = ORANGE,
			draw_radius = 50)

		sun1 = Body(
			name = "sun1",
			mass = 9.945e29,
			pos_x = 24_500_000, pos_y = 0,
			velocity_x = 0, velocity_y = -21_248.66363,
			pos_to_screen_pos = self.pos_to_screen_pos,
			color = ORANGE,
			draw_radius = 30)

		sun2 = Body(
			name = "sun2",
			mass = 9.945e29,
			pos_x = -24_500_000, pos_y = 0,
			velocity_x = 0, velocity_y = 21_248.66363,
			pos_to_screen_pos = self.pos_to_screen_pos,
			color = ORANGE,
			draw_radius = 30)

		earth = Body(
			name = "earth",
			mass = 5.972e24,
			pos_x = -147_090_000, pos_y = 0,
			velocity_x = 0, velocity_y = -30_000,
			pos_to_screen_pos = self.pos_to_screen_pos,
			color = BLUE,
			draw_radius = 14,
			draw_resulting_force =False,
			draw_other_forces = False)

		earth2 = Body(
			name = "earth2",
			mass = 5.972e24,
			pos_x = 0, pos_y = -147_090_000,
			velocity_x = 20_000, velocity_y = 0,
			pos_to_screen_pos = self.pos_to_screen_pos,
			color = BLUE,
			draw_radius = 5)

		moon = Body(
			name = "moon",
			mass = 7.346e22,
			pos_x = earth.pos_x - 384_000, pos_y = 0,
			velocity_x = 0, velocity_y = earth.velocity_y - 1_023,
			pos_to_screen_pos = self.pos_to_screen_pos,
			color = GREY,
			draw_radius = 5
		)

		self.bodies = [earth, moon, sun1, sun2]

		# init pygame
		pygame.init()
		self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE) # Create a window surface
		pygame.display.set_caption("Gravity simulation")


	# game

	def run(self):
		# initilize imgui context (see documentation)
		imgui.create_context()
		imgui.get_io().display_size = 100, 100
		imgui.get_io().fonts.get_tex_data_as_rgba32()
		
		while self.running:

			# calculate delta time of last frame
			delta = self.calc_delta()
			#print("Delta: ", delta)

			# handle input
			for event in pygame.event.get():
				self.handle_event(event)

			self.update(delta)
			self.render()

			pygame.display.flip()
			#print("FPS: ", (1000 / delta) if (delta > 0) else "infinite")
	
	def update(self, delta):
		# save the distance between fixed body and start values of the view
		if self.fixed_body is not None:
			last_pos_x = self.fixed_body.pos_x
			last_pos_y = self.fixed_body.pos_y

		# calculate forces
		for body in self.bodies:
			self.calc_force_on_body(body)

		# update bodies
		for body in self.bodies:
			body.update(delta)

		# update the view
		if self.fixed_body is not None:
			self.view_start_x += self.fixed_body.pos_x - last_pos_x
			self.view_start_y += (self.fixed_body.pos_y - last_pos_y) * self.window_width / self.window_height

	def render(self):
		self.screen.fill(BLACK)

		# draw background
		for star in self.background_stars:
			pygame.draw.circle(self.screen, (star[2], star[2], star[2]), self.pos_to_screen_pos(star[0], star[1]), star[3])

		#pygame.draw.line(self.screen, (200, 0, 100), (self.window_width / 2, 0), (self.window_width / 2, self.window_height)) # cross
		#pygame.draw.line(self.screen, (200, 0, 100), (0, self.window_height / 2), (self.window_width, self.window_height / 2))
		for body in self.bodies:
			body.draw(self.screen)


	# input

	def handle_event(self, event):
		# quit
		if event.type == pygame.QUIT:
			self.running = False

		# mouse
		elif event.type == pygame.MOUSEBUTTONDOWN:
			# primary button
			if event.button == 1:
				(mouse_x, mouse_y) = pygame.mouse.get_pos()
				self.mouse_clicked(mouse_x, mouse_y)

			# scrool up = zoom in
			if event.button == 4:
				self.zoom_in()

			# scroll down = zoom out
			elif event.button == 5:
				self.zoom_out()

		# window resize
		elif event.type == pygame.VIDEORESIZE:
			self.view_start_x += (0.5 * self.view_width * (1.0 / self.window_width - 1.0 / event.w))
			self.view_start_y = (event.w / event.h) * ((self.view_width * (0.5 * self.window_height + 0.5) + self.view_start_y * self.window_height) / self.window_width) - (0.5 * self.view_width * (1.0 + 1.0 / event.h))

			self.window_width = event.w
			self.window_height = event.h

	def mouse_clicked(self, mouse_x, mouse_y):
		for body in self.bodies:
			if self.is_click_on_body(body, mouse_x, mouse_y):
				self.fixed_body = body
				print("Clicked", self.fixed_body.name)
				return
		self.fixed_body = None


	# utility

	def calc_force_on_body(self, body):
		body.force_x = 0
		body.force_y = 0
		body.forces = []

		for other_body in self.bodies:
			if other_body is body: # don't calculate the force between the body and itself
				continue

			# vector from other_bodys positon to bodys position
			vec_x = other_body.pos_x - body.pos_x
			vec_y = other_body.pos_y - body.pos_y

			# magnitude of the force
			distance_squared = vec_x * vec_x + vec_y * vec_y
			force_magnitude = App.GRAVITATIONAL_CONSTANT * body.mass * other_body.mass / distance_squared

			# vector of the force
			scale_factor = force_magnitude / math.sqrt(distance_squared)
			force_x = vec_x * scale_factor
			force_y = vec_y * scale_factor

			body.forces.append((force_x, force_y))

			body.force_x += force_x
			body.force_y += force_y

	def zoom_in(self):
		self.zoom(1 / App.ZOOM_STEP)

	def zoom_out(self):
		self.zoom(App.ZOOM_STEP)

	def zoom(self, zoom_factor):
		# change the start values, so that the position where the mouse cursor is stayes the same after zoom
		(mouse_x, mouse_y) = pygame.mouse.get_pos()
		self.view_start_x += (1.0 - zoom_factor) * (mouse_x / self.window_width) * self.view_width
		self.view_start_y += (1.0 - zoom_factor) * (mouse_y / self.window_height) * self.view_width

		# change width of the view = zoom
		self.view_width *= zoom_factor

	def pos_to_screen_pos(self, pos_x, pos_y):
		screen_x = (pos_x - self.view_start_x) * self.window_width / self.view_width - 0.5
		screen_y = (pos_y * self.window_width - self.view_start_y * self.window_height) / self.view_width - 0.5

		return (screen_x, screen_y)

	#def screen_pos_to_pos(self, screen_x, screen_y):
	#	pos_x = self.view_width * (screen_x + 0.5) / self.window_width + self.view_start_x
	#	pos_y = (self.view_width * (screen_y + 0.5) + self.view_start_y * self.window_height) / self.window_width
	#	return (pos_x, pos_y)

	def is_click_on_body(self, body: Body, click_screen_x, click_screen_y):
		(body_screen_x, body_screen_y) = self.pos_to_screen_pos(body.pos_x, body.pos_y)
		screen_distance_squared = (body_screen_x - click_screen_x) ** 2 + (body_screen_y - click_screen_y) ** 2

		return (screen_distance_squared <= body.draw_radius ** 2)

	# TODO when zooming and resizing the background has to be changed
	def generate_background_stars(self):
		self.background_stars = []

		for i in range(0, random.randint(700, 1500)):
			pos_x = random.randint(int(self.view_start_x), int(self.view_start_x) + int(self.view_width))
			pos_y = random.randint(int(self.view_start_y), int(self.view_start_y) + int(self.view_width * (self.window_height / self.window_width)))
			brightness = random.randint(100, 255)

			if random.randint(0, 30) == 0:
				draw_radius = 3
			elif random.randint(0, 5) == 0:
				draw_radius = 2
			else:
				draw_radius = 1

			self.background_stars.append((pos_x, pos_y, brightness, draw_radius))


	def calc_delta(self):
		micros = datetime.now().microsecond

		if self.last_micros == 0:
			self.last_micros = micros
			return 0
		
		delta = micros - self.last_micros
		self.last_micros = micros
		if delta < 0:
			delta += 999999 # overflow

		return delta / 1000.0 # delta in ms
