import math
from datetime import datetime

import pygame
from pygame.constants import KMOD_LCTRL

from utility import *
from body import Body
from dynamic_background import DynamicBackground

class App:
	GRAVITATIONAL_CONSTANT = 6.67384e-20 # for calculating force in kg * km / s^2
	ZOOM_STEP = 1.03
	TIME_STEP = 1.3
	DRAW_FORCES_STEP = 1.2


	# init

	def __init__(self):
		self.running = True
		self.last_micros = 0
		
		self.window_width = 720 # size of the window
		self.window_height = 600
		self.view_width = 350_000_000 # size of the model
		self.view_start_x = -self.view_width / 2 # x-position (in the model) at the left edge of the window
		self.view_start_y = self.view_start_x * self.window_height / self.window_width
		self.fixed_body: Body = None # if this is a body, then the view always changes, so that the body is in a fixed place
		
		self.background = DynamicBackground(self.view_width, self.view_start_x, self.view_start_y, self.window_width / self.window_height, self.pos_to_screen_pos)
		self.init_model()
		self.draw_forces = False
		self.draw_forces_factor = 1.0

		self.time_factor = 1_577_847 # time needs to pass faster (1 year = 20s)
		self.paused = False
		self.draw_background = True

		# init pygame
		pygame.init()
		self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE) # Create a window surface
		pygame.display.set_caption("Gravity simulation")

	def init_model(self):
		self.sun = Body(
			name = "sun",
			mass = 1.989e30,
			pos_x = 0, pos_y = 0,
			velocity_x = 0, velocity_y = 0,
			draw_radius = 25,
			color = ORANGE,
			pos_to_screen_pos = self.pos_to_screen_pos,
		)

		self.sun1 = Body(
			name = "sun1",
			mass = 9.945e29,
			pos_x = 24_500_000, pos_y = 0,
			velocity_x = 0, velocity_y = -21_248.66363,
			draw_radius = 20,
			color = ORANGE,
			pos_to_screen_pos = self.pos_to_screen_pos,
		)

		self.sun2 = Body(
			name = "sun2",
			mass = 9.945e29,
			pos_x = -24_500_000, pos_y = 0,
			velocity_x = 0, velocity_y = 21_248.66363,
			draw_radius = 20,
			color = ORANGE,
			pos_to_screen_pos = self.pos_to_screen_pos,
		)

		mercury = Body(
			name = "mercury",
			mass = 3.285e23,
			pos_x = -69_817_000, pos_y = 0,
			velocity_x = 0, velocity_y = -38_860,
			draw_radius = 10,
			color = (188, 167, 116),
			pos_to_screen_pos = self.pos_to_screen_pos
		)

		venus = Body(
			name = "venus",
			mass = 4.8675e24,
			pos_x = -108_939_000, pos_y = 0,
			velocity_x = 0, velocity_y = -34_790,
			draw_radius = 10,
			color = (171, 105, 61),
			pos_to_screen_pos = self.pos_to_screen_pos
		)

		earth = Body(
			name = "earth",
			mass = 5.9724e24,
			pos_x = -152_099_000, pos_y = 0,
			velocity_x = 0, velocity_y = -29_290,
			draw_radius = 13,
			color = BLUE,
			pos_to_screen_pos = self.pos_to_screen_pos,
		)

		self.moon = Body(
			name = "moon",
			mass = 7.346e22,
			pos_x = earth.pos_x - 363_300, pos_y = 0,
			velocity_x = 0, velocity_y = earth.velocity_y - 970,
			draw_radius = 6,
			color = GREY,
			pos_to_screen_pos = self.pos_to_screen_pos,
		)

		mars = Body(
			name = "mars",
			mass = 6.4171e23,
			pos_x = -249_229_000, pos_y = 0,
			velocity_x = 0, velocity_y = -21_970,
			draw_radius = 10,
			color = (220, 59, 36),
			pos_to_screen_pos = self.pos_to_screen_pos
		)

		jupiter = Body(
			name = "jupiter",
			mass = 1898.19e24,
			pos_x = -816_618_000, pos_y = 0,
			velocity_x = 0, velocity_y = -12_440,
			draw_radius = 15,
			color = (184, 135, 125),
			pos_to_screen_pos = self.pos_to_screen_pos
		)

		saturn = Body(
			name = "saturn",
			mass = 568.34e24,
			pos_x = -1_514_504_000, pos_y = 0,
			velocity_x = 0, velocity_y = -9_090,
			draw_radius = 11,
			color = (206, 177, 121),
			pos_to_screen_pos = self.pos_to_screen_pos
		)

		uranus = Body(
			name = "uranus",
			mass = 86.813e24,
			pos_x = -3_003_625_000, pos_y = 0,
			velocity_x = 0, velocity_y = -6_490,
			draw_radius = 10,
			color = (0, 162, 252),
			pos_to_screen_pos = self.pos_to_screen_pos
		)

		neptune = Body(
			name = "neptune",
			mass = 102.413e24,
			pos_x = -4_545_671_000, pos_y = 0,
			velocity_x = 0, velocity_y = - 5_370,
			draw_radius = 10,
			color = (46, 62, 159),
			pos_to_screen_pos = self.pos_to_screen_pos
		)

		pluto = Body(
			name = "pluto",
			mass = 1.303e22,
			pos_x = -7_304_326_000, pos_y = 0,
			velocity_x = 0, velocity_y = - 3_710,
			draw_radius = 7,
			color = (149, 151, 163),
			pos_to_screen_pos = self.pos_to_screen_pos
		)

		self.bodies = [pluto, neptune, uranus, saturn, jupiter, mars, self.moon, earth, venus, mercury, self.sun]


	# game

	def run(self):
		while self.running:

			# calculate delta time of last frame
			delta = self.calc_delta()
			#print("Delta: ", delta)

			# handle input
			for event in pygame.event.get():
				self.handle_event(event)

			if not self.paused:
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
			body.update(delta * self.time_factor)

		# update the view for fixed body
		if self.fixed_body is not None:
			self.view_start_x += self.fixed_body.pos_x - last_pos_x
			self.view_start_y += self.fixed_body.pos_y - last_pos_y
			self.background.change_view_starts(self.view_start_x, self.view_start_y)

	def render(self):
		# reset the screen to black
		self.screen.fill(BLACK)

		# draw background
		if (self.draw_background):
			self.background.draw(self.screen)

		# draw all bodies
		for body in self.bodies:
			body.draw(self.screen, self.draw_forces_factor if self.draw_forces else 0)


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
			self.window_resize(event.w, event.h)

		# keys
		elif event.type == pygame.KEYDOWN:
			self.handle_key_down(event.key, event.mod)

	def handle_key_down(self, key, mod):
			# Ctrl + alt + Plus
			if (key == pygame.K_PLUS or key == pygame.K_KP_PLUS) and (mod & pygame.KMOD_LCTRL) and (mod & pygame.KMOD_LSHIFT) and self.draw_forces:
				self.draw_forces_factor *= App.DRAW_FORCES_STEP

			# Ctrl + alt + Minus
			elif (key == pygame.K_MINUS or key == pygame.K_KP_MINUS) and (mod & pygame.KMOD_LCTRL) and (mod & pygame.KMOD_LSHIFT) and self.draw_forces:
				self.draw_forces_factor /= App.DRAW_FORCES_STEP

			# Ctrl + Plus
			elif (key == pygame.K_PLUS or key == pygame.K_KP_PLUS) and (mod & pygame.KMOD_LCTRL):
				self.time_factor *= App.TIME_STEP

			# Ctrl + Minus
			elif (key == pygame.K_MINUS or key == pygame.K_KP_MINUS) and (mod & pygame.KMOD_LCTRL):
				self.time_factor /= App.TIME_STEP

			# Ctrl + Space
			elif key == pygame.K_SPACE and (mod & pygame.KMOD_LCTRL):
				self.paused = not self.paused

			# Ctrl + f
			elif key == pygame.K_f and (mod & pygame.KMOD_LCTRL):
				self.draw_forces = not self.draw_forces

			# Ctrl + b
			elif key == pygame.K_b and (mod & pygame.KMOD_LCTRL):
				self.draw_background = not self.draw_background

			# Ctrl + d
			elif key == pygame.K_d and (mod & pygame.KMOD_LCTRL):
				if self.sun in self.bodies:
					self.bodies.remove(self.sun)
					self.bodies.append(self.sun1)
					self.bodies.append(self.sun2)
				else:
					self.bodies.remove(self.sun1)
					self.bodies.remove(self.sun2)
					self.bodies.append(self.sun)

			# Ctrl + m
			elif key == pygame.K_m and (mod & pygame.KMOD_LCTRL):
				if self.fixed_body is not self.moon:
					self.fixed_body = self.moon
				else:
					self.fixed_body = None

			# Ctrl + Escape
			elif key == pygame.K_ESCAPE and (mod & pygame.KMOD_LCTRL):
				self.running = False

	def mouse_clicked(self, mouse_x, mouse_y):
		for body in reversed(self.bodies):
			if self.is_click_on_body(body, mouse_x, mouse_y):
				self.fixed_body = body
				return
		self.fixed_body = None

	def window_resize(self, new_width, new_height):
		self.view_start_x += 0.5 * self.view_width * (1.0 / self.window_width - 1.0 / new_width) # the pixel (with / 2, _) will correspond to the same position in the model before and after window resize (is almost the same as having the pixel (0, _) => is almost the same as doing nothing)
		self.view_start_y += 0.5 * self.view_width * ((self.window_height + 1.0) / self.window_width - (new_height + 1.0) / new_width) # the pixel (_, height / 2) will correspond to the same position in the model before and after window resize 

		self.window_width = new_width
		self.window_height = new_height

		# regenerate background (TODO implement other solution)
		self.background.view_start_x = self.view_start_x
		self.background.view_start_y = self.view_start_y
		self.background.screen_ratio = self.window_width / self.window_height
		self.background.stars = []
		self.background.generate()


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

		# update background
		self.background.zoom_in(self.view_width, self.view_start_x, self.view_start_y)

	def zoom_out(self):
		self.zoom(App.ZOOM_STEP)

		# update background
		self.rects = self.background.zoom_out(self.view_width, self.view_start_x, self.view_start_y)

	def zoom(self, zoom_factor):
		# change the start values, so that the position where the mouse cursor is stayes the same after zoom
		(mouse_x, mouse_y) = pygame.mouse.get_pos()
		self.view_start_x += (1.0 - zoom_factor) * (mouse_x / self.window_width) * self.view_width
		self.view_start_y += (1.0 - zoom_factor) * (mouse_y / self.window_width) * self.view_width

		# change width of the view = zoom
		self.view_width *= zoom_factor

	def length_to_screen_length(self, length):
		return length * self.window_width / self.view_width

	def pos_to_screen_pos(self, pos_x, pos_y):
		screen_x = (pos_x - self.view_start_x) * self.window_width / self.view_width - 0.5
		screen_y = (pos_y - self.view_start_y) * self.window_width / self.view_width - 0.5

		return (screen_x, screen_y)

	def screen_pos_to_pos(self, screen_x, screen_y):
		pos_x = self.view_width * (screen_x + 0.5) / self.window_width + self.view_start_x
		pos_y = self.view_width * (screen_y + 0.5) / self.window_width + self.view_start_y
		return (pos_x, pos_y)

	def is_click_on_body(self, body: Body, click_screen_x, click_screen_y):
		(body_screen_x, body_screen_y) = self.pos_to_screen_pos(body.pos_x, body.pos_y)
		screen_distance_squared = (body_screen_x - click_screen_x) ** 2 + (body_screen_y - click_screen_y) ** 2

		return (screen_distance_squared <= body.draw_radius ** 2)

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

	def is_key_pressed(key) -> bool:
		return pygame.key.get_mods() & key

	def is_left_ctrl_pressed() -> bool:
		return App.is_key_pressed(pygame.K_LCTRL)
