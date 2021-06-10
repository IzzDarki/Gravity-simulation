import pygame

class App:
	def __init__(self):
		pygame.init()
		self.running = True
		self.last_millis = -1
		self.screen = pygame.display.set_mode((1080, 720), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE) # Create a window surface
		pygame.display.set_caption("Gravity simulation")


	def run(self):
		while self.running:

			# Input
			for event in pygame.event.get():
				self.handle_event(event)

			delta = self.calc_delta()
			print("Delta: ", delta)
			# print("FPS: ", (1000 / delta) if (delta > 0) else "infinite")
			
		
	def handle_event(self, event):
		if event.type == pygame.QUIT:
			self.running = False

	# helpers
	def calc_delta(self):
		millis = pygame.time.get_ticks()

		if self.last_millis == -1:
			self.last_millis = millis
			return 0
		
		delta = millis - self.last_millis
		self.last_millis = millis
		return delta
