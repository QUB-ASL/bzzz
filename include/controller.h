#ifndef CONTROLLER_H
#define CONTROLLER_H

// I have the impression that "#pragma once" is not
// supported on ESP32

// Note that these variables use the prefix `c_` as they
// as global constants

const float c_lqr_gain[3] = {1.0, 2.0, 3.0}; /**< LQR Gain */
const float c_max_control_action = 10.;      /**< Minimum control action */
const float c_min_control_action = -10.;     /**< Maximum control action */

/**
 * @brief computes control action
 *
 * @param state_x state of the system
 *
 * @return control voltage
 */
float control_action(float state_x);

#endif /* CONTROLLER_H */
