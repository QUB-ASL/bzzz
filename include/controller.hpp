#include "config.hpp"

#ifndef CONTROLLER_H
#define CONTROLLER_H

// I have the impression that "#pragma once" is not
// supported on ESP32

namespace bzzz
{

    /**
     * @brief computes control action
     *
     * @param systemState state of the system
     *
     * @return control voltage
     */
    float controlAction(float systemState);
}
#endif /* CONTROLLER_H */
