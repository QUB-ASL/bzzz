from vector import Vector
from scalar import Scalar

class Quaternion:
    def __init__(self, q0, q1, q2, q3) -> None:
        self.q0 = Scalar(q0)
        self.vector = Vector(q1, q2, q3)