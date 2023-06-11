class ReferenceFrame:
    _is_global_frame_already_present = False
    _global_frame_object = None
    def __init__(self, x=0, y=0, z=0, set_as_global_reference = False) -> None:
        """Starts a co-ordinate frame centered at the give ordered triad (x, y, z). This triad should 
        be with respect to the given global reference frame.

        :param x: _description_
        :type x: _type_
        :param y: _description_
        :type y: _type_
        :param z: _description_
        :type z: _type_
        """
        if ReferenceFrame._is_global_frame_already_present:
            if set_as_global_reference:
                print(f"A global reference frame is already present. Setting as a generic reference frame at {x, y, z}.")
            self.x = x
            self.y = y
            self.z = z
            self.is_global_reference_frame = False
        else:
            if set_as_global_reference:
                if x != 0 or y != 0 or z != 0:
                    print(f"A global reference frame should be defined with an absolute center, not with {x, y, z}.\nForcing the frame to {0, 0, 0}.")
                self.x = 0
                self.y = 0
                self.z = 0
                self.is_global_reference_frame = True
                ReferenceFrame._is_global_frame_already_present = True
                ReferenceFrame._global_frame_object = self
            else:
                print("Cannot instantiate. A global reference frame has not been defined.\nDefine a global frame first using the 'set_as_global_reference' parameter.")
                self.__del__(True)

    def __del__(self, is_exception=False):
        if is_exception:
            raise Exception("The destructor is called. Did you try to define a generic reference frame prior to defining a global frame?")
        
    def __translate(self, X, Y, Z):
        pass

    def __rotate(self, quaternion):
        pass
    
if __name__ == '__main__':
    a = ReferenceFrame(1, 2, 3, set_as_global_reference=True)
    b = ReferenceFrame(1, 2, 3, set_as_global_reference=True)
