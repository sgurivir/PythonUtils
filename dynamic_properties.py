

class Cube(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @property
    def area(self):
        return self.x * self.y * self.z


a = Cube(2, 3, 4)
print a.area
