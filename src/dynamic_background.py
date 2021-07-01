import random
from types import MethodType

import pygame
from pygame import Rect, draw

from utility import Rectangle

class DynamicBackground:

	class Star:
		def __init__(self, pos_x, pos_y, brightness, draw_radius):
			self.pos_x = pos_x
			self.pos_y = pos_y
			self.brightness = brightness
			self.draw_radius = draw_radius

	def __init__(self, view_width, view_start_x, view_start_y, screen_ratio, pos_to_screen_pos: MethodType):
		self.view_width = view_width
		self.view_start_x = view_start_x
		self.view_start_y = view_start_y
		self.screen_ratio = screen_ratio # width / height
		self.stars = []
		self.pos_to_screen_pos: MethodType = pos_to_screen_pos

		self.generate()


	# functions to generate or update the stars

	def generate(self):
		for i in range(0, random.randint(400, 900)):
			self.stars.append(self.generate_star())

	def zoom_in(self, new_view_width, new_view_start_x, new_view_start_y):
		# Expects that the new view width is smaller than the old one
		# start_x has to be bigger than (right to) the old one
		# start_y has to be bigger than (above) the old one

		new_view_end_x = DynamicBackground.get_end_x(new_view_start_x, new_view_width)
		new_view_end_y = self.get_end_y(new_view_start_y, new_view_width)

		# Rectangle that represents the new view
		new_view = Rectangle(new_view_start_x, new_view_end_x, new_view_start_y, new_view_end_y)

		# Move all stars that got out of sight back into sight
		for star in self.stars:
			if star.pos_x < new_view_start_x or star.pos_x > new_view_end_x or star.pos_y < new_view_start_y or star.pos_y > new_view_end_y:
				(star.pos_x, star.pos_y) = DynamicBackground.random_pos_in_rect(new_view)

		# Update
		self.view_width = new_view_width
		self.view_start_x = new_view_start_x
		self.view_start_y = new_view_start_y

	def zoom_out(self, new_view_width, new_view_start_x, new_view_start_y):
		# Expects the new view width to be bigger than the old one
		# start_x has to be smaller than (left to) the old one
		# start_y has to be smaller than (above) the old one

		new_view_end_x = DynamicBackground.get_end_x(new_view_start_x, new_view_width)
		old_view_end_x = DynamicBackground.get_end_x(self.view_start_x, self.view_width)
		new_view_end_y = self.get_end_y(new_view_start_y, new_view_width)
		old_view_end_y = self.get_end_y(self.view_start_y, self.view_width)

		# Calculate all 4 rectangles where stars get moved to
		rect_left = Rectangle(new_view_start_x, self.view_start_x, new_view_start_y, new_view_end_y)
		rect_right = Rectangle(old_view_end_x, new_view_end_x, new_view_start_y, new_view_end_y)
		rect_top = Rectangle(self.view_start_x, old_view_end_x, new_view_start_y, self.view_start_y)
		rect_bottom = Rectangle(self.view_start_x, old_view_end_x, old_view_end_y, new_view_end_y)

		# Calculate number of stars to move
		new_area = new_view_width * new_view_width / self.screen_ratio
		old_area = self.view_width * self.view_width / self.screen_ratio
		keep_stars_count = int((old_area / new_area) * len(self.stars))

		# Calculate probability for each rectangle
		total_rect_area = new_area - old_area
		rect_left_prabability = rect_left.get_area() / total_rect_area
		rect_right_probability = rect_right.get_area() / total_rect_area
		rect_top_probability = rect_top.get_area() / total_rect_area
		rect_bottom_probability = rect_bottom.get_area() / total_rect_area
		rect_probabilities = [rect_left_prabability, rect_right_probability, rect_top_probability, rect_bottom_probability]

		# Create a list of stars that will be moved
		move_stars_list = random.sample(self.stars, len(self.stars) - keep_stars_count)

		# Move every star in the previously created list
		for star in move_stars_list:
			# Select one of the rects and set star to a random position in this rect
			rect_num = DynamicBackground.random_num_with_probability(rect_probabilities)
			if rect_num == 0:
				(star.pos_x, star.pos_y) = DynamicBackground.random_pos_in_rect(rect_left)
			elif rect_num == 1:
				(star.pos_x, star.pos_y) = DynamicBackground.random_pos_in_rect(rect_right)
			elif rect_num == 2:
				(star.pos_x, star.pos_y) = DynamicBackground.random_pos_in_rect(rect_top)
			else:
				(star.pos_x, star.pos_y) = DynamicBackground.random_pos_in_rect(rect_bottom)
			
		new_view = Rectangle(new_view_start_x, new_view_end_x, new_view_start_y, new_view_end_y)
		old_view = Rectangle(self.view_start_x, old_view_end_x, self.view_start_y, old_view_end_y)

		# Update
		self.view_width = new_view_width
		self.view_start_x = new_view_start_x
		self.view_start_y = new_view_start_y

	def change_view_starts(self, new_view_start_x, new_view_start_y):
		new_view_end_x = DynamicBackground.get_end_x(new_view_start_x, self.view_width)
		old_view_end_x = DynamicBackground.get_end_x(self.view_start_x, self.view_width)
		new_view_end_y = self.get_end_y(new_view_start_y, self.view_width)
		old_view_end_y = self.get_end_y(self.view_start_y, self.view_width)

		# Calculate both rectangles where stars have to be moved to
		if new_view_start_x < self.view_start_x:
			rect_horizontal = Rectangle(new_view_start_x, self.view_start_x, new_view_start_y, new_view_end_y)
		else:
			rect_horizontal = Rectangle(old_view_end_x, new_view_end_x, new_view_start_y, new_view_end_y)

		if new_view_start_y < self.view_start_y:
			rect_vertical = Rectangle(self.view_start_x, old_view_end_x, new_view_start_y, self.view_start_y)
		else:
			rect_vertical = Rectangle(self.view_start_x, old_view_end_x, old_view_end_y, new_view_end_y)

		# Calculate probability for each rectangle
		total_new_area = rect_horizontal.get_area() + rect_vertical.get_area()
		rect_horizontal_probability = rect_horizontal.get_area() / total_new_area
		rect_vertical_probability = rect_vertical.get_area() / total_new_area
		rect_probabilities = [rect_horizontal_probability, rect_vertical_probability]

		# Move every star that is out of sight to one of the new rectangles
		for star in self.stars:
			if star.pos_x < new_view_start_x or star.pos_x > new_view_end_x or star.pos_y < new_view_start_y or star.pos_y > new_view_end_y:
				rand = DynamicBackground.random_num_with_probability(rect_probabilities)
				if rand == 0:
					(star.pos_x, star.pos_y) = DynamicBackground.random_pos_in_rect(rect_horizontal)
				else:
					(star.pos_x, star.pos_y) = DynamicBackground.random_pos_in_rect(rect_vertical)

		# Update
		self.view_start_x = new_view_start_x
		self.view_start_y = new_view_start_y


	# helpers

	def get_end_x(view_start_x, view_width):
		return view_start_x + view_width

	def get_end_y(self, view_start_y, view_width):
		return view_start_y + view_width / self.screen_ratio

	def generate_star_pos(self):
		pos_x = random.randint(int(self.view_start_x), int(self.view_start_x + self.view_width))
		pos_y = random.randint(int(self.view_start_y), int(self.view_start_y + self.view_width / self.screen_ratio))
		return (pos_x, pos_y)

	def generate_brightness():
		return random.randint(100, 255)

	def generate_draw_radius():
		random_num = random.randint(0, 29)
		if random_num == 29:
			return 3 # p = 1/30
		elif random_num < 6:
			return 2 # p = 1/5 
		else:
			return 1

	def generate_star_pos_x(self, start_x_diff, new_view_start_x, end_x_diff, new_view_end_x, old_view_end_x):
		if start_x_diff > 0 and end_x_diff > 0:
			if random.randint(0, 1) == 0:
				pos_x = random.randint(new_view_start_x, self.view_start_x) # generate new position on the left side
			else:
				pos_x = random.randint(old_view_end_x, new_view_end_x) # generate new position on the right side
		elif end_x_diff <= 0:
			pos_x = random.randint(new_view_start_x, self.view_start_x) # generate new position on the left side
		else:
			pos_x = random.randint(old_view_end_x, new_view_end_x) # generate new position on the right side

		return pos_x

	def generate_star_pos_y(self, start_y_diff, new_view_start_y, end_y_diff, new_view_end_y, old_view_end_y):
		if start_y_diff > 0 and end_y_diff > 0:
			if random.randint(0, 1) == 0:
				pos_y = random.randint(new_view_start_y, self.view_start_y) # generate new position on top
			else:
				pos_y = random.randint(old_view_end_y, new_view_end_y) # generate new position on bottom
		elif end_y_diff <= 0:
			pos_y = random.randint(new_view_start_y, self.view_start_y) # generate new position on top
		else:
			pos_y = random.randint(old_view_end_y, new_view_end_y) # generate new position on bottom

		return pos_y

	def generate_star(self) -> Star:
		(pos_x, pos_y) = self.generate_star_pos()
		brightness = DynamicBackground.generate_brightness()
		draw_radius = DynamicBackground.generate_draw_radius()

		return DynamicBackground.Star(pos_x, pos_y, brightness, draw_radius)

	def draw(self, screen):
		for star in self.stars:
			pygame.draw.circle(screen, (star.brightness, star.brightness, star.brightness), self.pos_to_screen_pos(star.pos_x, star.pos_y), star.draw_radius)


	# random generator functions
	
	def random_num_with_probability(probability_list):
		rand = random.randint(0, 999_999)
		for i in range(0, len(probability_list)):
			absolute_probability = probability_list[i] * 999_999
			if rand < absolute_probability:
				return i
			else:
				rand -= absolute_probability
	
	def random_pos_in_rect(rect: Rectangle):
		x = random.randint(rect.start_x, rect.end_x)
		y = random.randint(rect.start_y, rect.end_y)
		return (x, y)