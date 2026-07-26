#include "fdi.hpp"

namespace bzzz
{
    ResidualCost::ResidualCost()
    {
        m_head = 0;
        m_count = 0;
        for (int c = 0; c < 7; c++) m_sum[c] = 0.0f;
        for (int j = 0; j < W; j++)
            for (int c = 0; c < 7; c++) m_buf[j][c] = 0.0f;
    }

    float ResidualCost::push(const float *resQ, const float *resW, const float *sigma)
    {
        float sample[7] = {
            resQ[0], resQ[1], resQ[2], resQ[3],  // qw qx qy qz
            resW[0], resW[1], resW[2]            // wx wy wz
        };

        float sq[7];
        for (int c = 0; c < 7; c++)
        {
            float n = sample[c] / sigma[c];
            sq[c] = n * n;
        }

        for (int c = 0; c < 7; c++)
        {
            m_sum[c] -= m_buf[m_head][c];
            m_buf[m_head][c] = sq[c];
            m_sum[c] += sq[c];
        }

        m_head = (m_head + 1) % W;
        if (m_count < W) m_count++;

        float J = 0.0f;
        for (int c = 0; c < 7; c++) J += m_sum[c];
        return J;
    }
}