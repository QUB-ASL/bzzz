#include "config.hpp"
#include "quaternion.hpp"

#ifndef PREDICTION_H
#define PREDICTION_H

#ifndef PREDICTION_HORIZON
#define PREDICTION_HORIZON 1
#endif

namespace bzzz
{
    /**
     * Closed-loop N-step-ahead predictor for FDI.
     *
     * Each control step it (a) compares the prediction made N steps ago
     * against the current measurement, and (b) pushes a fresh N-step
     * prediction into a ring buffer.
     *
     * Motor order throughout: FR, FL, ML, BL, BR, MR
     */
    class Predictor
    {
    private:
        static const int H = PREDICTION_HORIZON;

        float m_gamma[6];        // motor health; 1 = healthy
        float m_B[3][6];         // thrust -> body torque
        float m_mix[6][3];       // control -> per-motor pwm delta

        float m_kq, m_kwXY, m_kwZ;
        float m_scale;           // controlToPwmScaling
        float m_clipLo, m_clipHi;

        float m_bufQ[H][4];
        float m_bufW[H][3];
        bool  m_bufValid[H];
        int   m_head;

        float m_resQ[4], m_resW[3];
        float m_matQ[4], m_matW[3];
        bool  m_haveResidual;

    public:
        Predictor();

        /** @brief motor health vector; H0 = all ones, H2 = FL failed, etc. */
        void setGamma(const float *gamma);

        /** @brief live controller gains, exactly as passed to Controller */
        void setGains(float kq, float kwXY, float kwZ);

        /** @brief pwm scaling and clip limits used by the flown mixer */
        void setPwmMapping(float scale, float clipLo, float clipHi);

        /**
         * @brief one control step
         * @param qMeas      measured attitude (relativeQuaternion)
         * @param wMeasDeg   measured body rates [deg/s]
         * @param throttle   throttle reference [pwm]
         * @param rollRef    roll reference [rad]
         * @param pitchRef   pitch reference [rad]
         * @param yawRef     yaw reference [rad]
         * @param yawRateRef yaw rate reference [rad/s]
         * @param dt         step time [s]
         */
        void step(const Quaternion &qMeas, const float *wMeasDeg,
          const float *pwmActual, float pwmOffset, float dt);

        /** @return true iff a matured prediction was available this step */
        bool residual(float *resQ, float *resW) const;

        /** @brief the N-step-old prediction that residual() compared against */
        void maturedPrediction(float *qOut, float *wOutDeg) const;

        bool haveResidual() const { return m_haveResidual; }
    };

} /* namespace bzzz */

#endif /* PREDICTION_H */