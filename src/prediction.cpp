#include "prediction.hpp"
#include <math.h>

namespace bzzz
{
    // ---------------- vehicle parameters ----------------
    static const float IX = 0.022f, IY = 0.022f, IZ = 0.042f;   // kg m^2
    static const float ARM_L = 0.35f;                          // m
    static const float KF = 1.5e-6f;                           // N / (pwm-900)^2, measured via scale                          // N / pwm^2
    static const float KM = 2.50e-8f;                           // Nm / pwm^2
    static const float KD[3] = {0.020f, 0.020f, 0.025f};

    static const float PSI_DEG[6] = {-30.f, 30.f, 90.f, 150.f, 210.f, 270.f};
    static const float SPIN[6]    = {  1.f, -1.f,  1.f,  -1.f,   1.f,  -1.f};

    // mixer, transcribed from controller.cpp; columns are [roll, pitch, yaw]
    static const float MIX[6][3] = {
        { -0.1340f,  0.5000f, -0.1340f },   // FR
        {  0.1340f,  0.5000f,  0.1340f },   // FL
        {  0.2679f,  0.0000f, -0.2321f },   // ML
        {  0.1340f, -0.5000f,  0.1340f },   // BL
        { -0.1340f, -0.5000f, -0.1340f },   // BR
        { -0.2679f,  0.0000f,  0.2321f }    // MR
    };

    static const float D2R = 0.01745329252f;
    static const float R2D = 57.2957795131f;

    static void quatMul(const float *a, const float *b, float *c)
    {
        c[0] = a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3];
        c[1] = a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2];
        c[2] = a[0]*b[2] - a[1]*b[3] + a[2]*b[0] + a[3]*b[1];
        c[3] = a[0]*b[3] + a[1]*b[2] - a[2]*b[1] + a[3]*b[0];
    }

    Predictor::Predictor()
    {
        m_head = 0;
        m_haveResidual = false;
        m_kq = m_kwXY = m_kwZ = 0.0f;
        m_scale = 300.0f;
        m_clipLo = 900.0f;
        m_clipHi = 2000.0f;

        for (int i = 0; i < 6; i++)
        {
            m_gamma[i] = 1.0f;
            float psi = PSI_DEG[i] * D2R;
            m_B[0][i] = ARM_L * sinf(psi);
            m_B[1][i] = ARM_L * cosf(psi);
            m_B[2][i] = SPIN[i] * (KM / KF);
            for (int j = 0; j < 3; j++) m_mix[i][j] = MIX[i][j];
        }
        for (int k = 0; k < H; k++) m_bufValid[k] = false;
    }

    void Predictor::setGamma(const float *gamma)
    {
        for (int i = 0; i < 6; i++) m_gamma[i] = gamma[i];
    }

    void Predictor::setGains(float kq, float kwXY, float kwZ)
    {
        m_kq = kq; m_kwXY = kwXY; m_kwZ = kwZ;
    }

    void Predictor::setPwmMapping(float scale, float clipLo, float clipHi)
    {
        m_scale = scale; m_clipLo = clipLo; m_clipHi = clipHi;
    }

        void Predictor::step(const Quaternion &qMeas, const float *wMeasDeg,
                    const float *pwmActual, float pwmOffset, float dt)
    {
        // ---- (a) mature: compare the prediction made H steps ago ----
        m_haveResidual = m_bufValid[m_head];
        if (m_haveResidual)
        {
            for (int i = 0; i < 4; i++)
            {
                m_matQ[i] = m_bufQ[m_head][i];
                m_resQ[i] = qMeas[i] - m_matQ[i];
            }
            for (int i = 0; i < 3; i++)
            {
                m_matW[i] = m_bufW[m_head][i];
                m_resW[i] = wMeasDeg[i] - m_matW[i];
            }
        }

        // ---- (b) fresh H-step prediction from the current measurement ----

        // reference quaternion, constant over the horizon
               float q[4] = { qMeas[0], qMeas[1], qMeas[2], qMeas[3] };
        float w[3] = { wMeasDeg[0]*D2R, wMeasDeg[1]*D2R, wMeasDeg[2]*D2R };

        for (int n = 0; n < H; n++)
        {
            // open-loop: use the actual PWM already written to the ESCs,
            // scaled per-hypothesis by gamma. No control-law re-simulation.
             float tau[3] = {0.0f, 0.0f, 0.0f};
            for (int i = 0; i < 6; i++)
            {
                float pwmEff = pwmActual[i] - pwmOffset;
                float F = m_gamma[i] * KF * pwmEff * pwmEff;
                tau[0] += m_B[0][i] * F;
                tau[1] += m_B[1][i] * F;
                tau[2] += m_B[2][i] * F;
            }
            // J wdot = tau - Kd w - w x (J w)
            float Jw[3] = { IX*w[0], IY*w[1], IZ*w[2] };
            float crs[3] = { w[1]*Jw[2] - w[2]*Jw[1],
                             w[2]*Jw[0] - w[0]*Jw[2],
                             w[0]*Jw[1] - w[1]*Jw[0] };
            w[0] += dt * (tau[0] - KD[0]*w[0] - crs[0]) / IX;
            w[1] += dt * (tau[1] - KD[1]*w[1] - crs[1]) / IY;
            w[2] += dt * (tau[2] - KD[2]*w[2] - crs[2]) / IZ;

            // qdot = 0.5 q (x) [0, w]
            float wq[4] = { 0.0f, w[0], w[1], w[2] };
            float qd[4];
            quatMul(q, wq, qd);

            float n2 = 0.0f;
            for (int i = 0; i < 4; i++) { q[i] += 0.5f*qd[i]*dt; n2 += q[i]*q[i]; }
            n2 = sqrtf(n2);
            if (n2 < 1e-9f) n2 = 1.0f;
            for (int i = 0; i < 4; i++) q[i] /= n2;
        }

        for (int i = 0; i < 4; i++) m_bufQ[m_head][i] = q[i];
        m_bufW[m_head][0] = w[0]*R2D;
        m_bufW[m_head][1] = w[1]*R2D;
        m_bufW[m_head][2] = w[2]*R2D;
        m_bufValid[m_head] = true;

        m_head = (m_head + 1) % H;
    }

    bool Predictor::residual(float *resQ, float *resW) const
    {
        if (!m_haveResidual) return false;
        for (int i = 0; i < 4; i++) resQ[i] = m_resQ[i];
        for (int i = 0; i < 3; i++) resW[i] = m_resW[i];
        return true;
    }

    void Predictor::maturedPrediction(float *qOut, float *wOutDeg) const
    {
        for (int i = 0; i < 4; i++) qOut[i] = m_matQ[i];
        for (int i = 0; i < 3; i++) wOutDeg[i] = m_matW[i];
    }

} /* namespace bzzz */