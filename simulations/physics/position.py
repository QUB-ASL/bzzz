from vector import Vector

class Position(Vector):
    def __init__(self, x, y, z):
        """instantiates a position vector

        :param x: x component of the vector
        :param y: y component of the vector
        :param z: z component of the vector
        """
        self.x = x
        self.y = y
        self.z = z




if __name__ == '__main__':
    a = Position(2, 3, 4)
    b = Vector(1, 2, 3)
    print(a * b)
    print((a @ b @ a) * a * b)
        