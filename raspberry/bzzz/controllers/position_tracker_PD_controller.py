import numpy as np
import math

class PositionTrackerPDController:
    def __init__(self, kp=0., kd=0., control_action_range=np.array([-0.01, 0.01])) -> None:
        self.__kappa = np.zeros((2, 4))
        self.__kappa[0, 0] = -kp
        self.__kappa[0, 2] = -kd
        self.__kappa[1, 1] = kp
        self.__kappa[1, 3] = kd
        self.__control_action_range = control_action_range
        self.__x_bar_u_bar = np.array([[0], [0], [0], [0]])

    def __update_kp_and_kd(self, kp, kd):
        if kp != None:
            self.__kappa[0, 0] = -kp
            self.__kappa[1, 1] = kp
        if kd != None:
            self.__kappa[0, 2] = -kd
            self.__kappa[1, 3] = kd

    def __update_x_bar_u_bar(self, reference_position_xy=np.array([[0], [0]])):
        self.__x_bar_u_bar[:2, 0] = reference_position_xy[:, 0]

    def control_action(self, current_state_estimates_xy_vxvy=np.array([[0], [0], [0], [0]]), current_heading_rad=0., reference_position_xy=np.array([[0], [0]]), kp=None, kd=None):
        self.__update_kp_and_kd(kp, kd)
        self.__update_x_bar_u_bar(reference_position_xy)

        error = current_state_estimates_xy_vxvy - self.__x_bar_u_bar
        error[0, 0] = -error[0, 0]*math.sin(current_heading_rad) + error[1, 0]*math.cos(current_heading_rad)
        error[1, 0] = error[0, 0]*math.cos(current_heading_rad) + error[1, 0]*math.sin(current_heading_rad)
        control_action =  self.__kappa@error
        
        control_action[0, 0] = math.asin(max(min(control_action[0, 0], self.__control_action_range[1]), self.__control_action_range[0]))
        control_action[1, 0] = math.asin(max(min(control_action[1, 0], self.__control_action_range[1]), self.__control_action_range[0]))

        # gives you (roll_rad, pitch_rad) commands
        return control_action

    

if __name__ == "__main__":
    PD = PositionTrackerPDController(0.0765, 0.01)
    print(PD.control_action(
        np.array([[0], [0], [1.49940899e-02], [0]]), -math.pi/2,
        np.array([[1], [1]])))
    # print(PD.control_action(
    #     np.array([[1.12496321e-02], [1], [1.49940899e-02], [0]]),
    #     np.array([[1.27996721e-02], [1]])))