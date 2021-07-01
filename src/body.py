from types import MethodType

import pygame

import utility

class Body:
	FORCE_TO_PIXELS = 1e-18

	def __init__(self, name, mass, pos_x: int, pos_y: int, velocity_x, velocity_y, draw_radius, color, pos_to_screen_pos: MethodType):
		self.name = name
		self.mass = mass # in kg
		self.pos_x: int = pos_x
		self.pos_y: int = pos_y
		self.velocity_x = velocity_x # in m / s
		self.velocity_y = velocity_y # in m / s
		self.draw_radius = draw_radius
		self.color = color

		self.pos_to_screen_pos: MethodType = pos_to_screen_pos

		self.force_x = 0 # in kg * km / s^2
		self.force_y = 0 # in kg * km / s^2
		self.forces = []

	def update(self, delta_time):
		# update velocity
		self.velocity_x = self.velocity_x + self.force_x * delta_time / self.mass
		self.velocity_y = self.velocity_y + self.force_y * delta_time / self.mass

		# update position
		self.pos_x = int(self.pos_x + delta_time / 1_000_000 * self.velocity_x) # need conversion because velocity is in m/s and not in km/ms
		self.pos_y = int(self.pos_y + delta_time / 1_000_000 * self.velocity_y) # need conversion because velocity is in m/s and not in km/ms

	def draw(self, screen, draw_forces_factor):
		# convert position in the model to coordinates on screen
		(pos_screen_x, pos_screen_y) = self.pos_to_screen_pos(self.pos_x, self.pos_y)

		# draw forces
		if draw_forces_factor > 0:
			self.draw_force(screen, pos_screen_x, pos_screen_y, self.force_x, self.force_y, draw_forces_factor, 2)

			for (force_x, force_y) in self.forces:
				self.draw_force(screen, pos_screen_x, pos_screen_y, force_x, force_y, draw_forces_factor)

		# draw the body
		pygame.draw.circle(screen, self.color, (pos_screen_x, pos_screen_y), self.draw_radius)

	def draw_force(self, screen, pos_screen_x, pos_screen_y, force_x, force_y, draw_force_factor, line_width = 1):
		(force_screen_x, force_screen_y) = (force_x * Body.FORCE_TO_PIXELS * draw_force_factor, force_y * Body.FORCE_TO_PIXELS * draw_force_factor)
		pygame.draw.line(screen, self.color, (pos_screen_x, pos_screen_y), (pos_screen_x + force_screen_x, pos_screen_y + force_screen_y), line_width)
		