# Colors
ORANGE = (255, 140, 0)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
GREY = (200, 200, 200)

class Rectangle:
    def __init__(self, start_x, end_x, start_y, end_y):
        self.start_x: int = int(start_x)
        self.end_x: int = int(end_x)
        self.start_y: int = int(start_y)
        self.end_y: int = int(end_y)

        if start_x > end_x:
            exit("start_x > end_x")
        elif start_y > end_y:
            exit("start_y > end_y")

    def get_width(self):
        return self.end_x - self.start_x

    def get_height(self):
        return self.end_y - self.start_y

    def get_area(self):
        return self.get_width() * self.get_height()