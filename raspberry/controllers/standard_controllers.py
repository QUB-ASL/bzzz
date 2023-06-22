def PD_controller(kp, kd, state_ref, state, state_dot_ref, state_dot):
    control_action = kp*(state_ref - state) + kd*(state_dot_ref - state_dot)
    return control_action

def PID_controller(kp, kd, ki, state_ref, state, state_dot_ref, state_dot, state_dash_ref, state_dash):
    control_action = PD_controller(kp, kd, state_ref, state, state_dot_ref, state_dot) + ki*(state_dash_ref - state_dash)
    return control_action