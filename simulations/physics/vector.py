from math import sqrt

class Vector:
    def __init__(self, x, y, z) -> None:
        """instantiates a vector

        :param x: x component of the vector
        :param y: y component of the vector
        :param z: z component of the vector
        """
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        """Perform vector addition.

        :param other: Other Vector object.
        :raises TypeError: When the other object is not a Vector.
        :return: Vector sum.
        """
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        raise TypeError
    
    def __str__(self):
        """String format of the vector components as an ordered triad (x, y, z).

        :return: Formatted Vector string.
        """
        return f"{self.x, self.y, self.z}"
    
    def __sub__(self, other):
        """Perform vector subtraction.

        :param other: Other Vector object.
        :raises TypeError: When the other object is not a Vector.
        :return: Vector subtraction.
        """
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        raise TypeError
        
    def __neg__(self):
        """Find the antiparallel vector.

        :return: The antiparallel vector.
        """
        return Vector(-self.x, -self.y, -self.z)
    
    def __pos__(self):
        """Find the parallel vector.

        :return: Same vector.
        """
        return Vector(self.x, self.y, self.z)
    
    def __mul__(self, other):
        """Vector dot product of two vectors or if the other is a scalar, returns the scaled vector.

        :param other: Vector object or scalar (int or float).
        :raises TypeError: If the other is not a Vector or scalar.
        :return: Either the Vector dot product, the reuslt is a scalar.
                    or Scaled vector.
        """
        if isinstance(other, Vector):
            return self.x*other.x + self.y*other.y + self.z*other.z
        elif isinstance(other, (int, float)):
            return Vector(other*self.x, other*self.y, other*self.z)
        raise TypeError
    
    def __rmul__(self, other):
        """Same as Vector dot product

        :param other: Vector object or scalar (int or float).
        :raises TypeError: If the other is not a Vector or scalar.
        :return: Either the Vector dot product, the reuslt is a scalar.
                    or Scaled vector.
        """
        return self.__mul__(other)
    
    def __matmul__(self, other):
        """Vector cross product of two vectors.

        :param other: Vector object.
        :raises TypeError: If the other is not a Vector.
        :return: Vector cross product, the reuslt is another vector which is perpendicular to the plane comprising the initial two vectors.
        """
        if isinstance(other, Vector):
            return Vector(self.y*other.z - self.z*other.y, -(self.x*other.z - self.z*other.x), self.x*other.y - self.y*other.x)
        raise TypeError
    
    def __abs__(self):
        return sqrt(self.z**2 + self.y**2 + self.z**2)
    
