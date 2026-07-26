#include "predictor.hpp"
#include <cmath>

namespace bzzz
{

//---------------------------------------------------------------------
// Tarot 680 PRO estimated inertia (kg·m²)
//---------------------------------------------------------------------
static constexpr float Ixx = 0.025f;
static constexpr float Iyy = 0.025f;
static constexpr float Izz = 0.045f;

//---------------------------------------------------------------------
// Torque scaling
// (Replace later with the actual motor/propeller model if available)
//---------------------------------------------------------------------
static constexpr float TORQUE_SCALING = 0.05f;

VehicleState VehiclePredictor::predict(
    const VehicleState& current,
    const float motorCommand[6],
    const ActuatorHealth& health,
    float dt)
{
    VehicleState predicted;

    //-----------------------------------------------------------------
    // 1. Apply actuator effectiveness Γ
    //-----------------------------------------------------------------

    float uFR = motorCommand[0] * health.gamma[0];
    float uFL = motorCommand[1] * health.gamma[1];
    float uML = motorCommand[2] * health.gamma[2];
    float uBL = motorCommand[3] * health.gamma[3];
    float uBR = motorCommand[4] * health.gamma[4];
    float uMR = motorCommand[5] * health.gamma[5];

    //-----------------------------------------------------------------
    // 2. Compute body torques
    //-----------------------------------------------------------------

    float tauX =
          0.5f*uFL
        + 0.5f*uFR
        - 0.5f*uBL
        - 0.5f*uBR;

    float tauY =
          uML
        - uMR
        + 0.8660254f*uFL
        + 0.8660254f*uBL
        - 0.8660254f*uBR
        - 0.8660254f*uFR;

    float tauZ =
          uFR
        - uFL
        + uML
        - uBL
        + uBR
        - uMR;

    float Tx = TORQUE_SCALING * tauX;
    float Ty = TORQUE_SCALING * tauY;
    float Tz = TORQUE_SCALING * tauZ;

    //-----------------------------------------------------------------
    // 3. Euler rigid-body rotational dynamics
    //-----------------------------------------------------------------

    float wx = current.omega[0];
    float wy = current.omega[1];
    float wz = current.omega[2];

    float alphaX =
        (Tx - (Izz - Iyy)*wy*wz) / Ixx;

    float alphaY =
        (Ty - (Ixx - Izz)*wx*wz) / Iyy;

    float alphaZ =
        (Tz - (Iyy - Ixx)*wx*wy) / Izz;

    //-----------------------------------------------------------------
    // 4. Integrate angular velocity
    //-----------------------------------------------------------------

    predicted.omega[0] = wx + alphaX*dt;
    predicted.omega[1] = wy + alphaY*dt;
    predicted.omega[2] = wz + alphaZ*dt;

//-----------------------------------------------------------------
// 5. Integrate quaternion
//-----------------------------------------------------------------

float q0 = current.attitude[0];
float q1 = current.attitude[1];
float q2 = current.attitude[2];
float q3 = current.attitude[3];

float dq0 =
    0.5f*(-q1*wx - q2*wy - q3*wz);

float dq1 =
    0.5f*( q0*wx + q2*wz - q3*wy);

float dq2 =
    0.5f*( q0*wy - q1*wz + q3*wx);

float dq3 =
    0.5f*( q0*wz + q1*wy - q2*wx);

predicted.attitude[0] = q0 + dq0*dt;
predicted.attitude[1] = q1 + dq1*dt;
predicted.attitude[2] = q2 + dq2*dt;
predicted.attitude[3] = q3 + dq3*dt;

//-----------------------------------------------------------------
// 6. Normalize quaternion
//-----------------------------------------------------------------

float norm =
    std::sqrt(
        predicted.attitude[0] * predicted.attitude[0] +
        predicted.attitude[1] * predicted.attitude[1] +
        predicted.attitude[2] * predicted.attitude[2] +
        predicted.attitude[3] * predicted.attitude[3]);

if(norm > 1e-6f)
{
    predicted.attitude[0] /= norm;
    predicted.attitude[1] /= norm;
    predicted.attitude[2] /= norm;
    predicted.attitude[3] /= norm;
}

    return predicted;
}

}