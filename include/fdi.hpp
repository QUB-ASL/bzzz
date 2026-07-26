#ifndef FDI_H
#define FDI_H

namespace bzzz
{
    /**
     * Sliding-window weighted residual cost:
     *   J = sum over the window of sum_c ( v(c) / sigma(c) )^2
     * channels c = [qw qx qy qz wx wy wz]
     */
    class ResidualCost
    {
    private:
        static const int W = 15;
        float m_buf[W][7];
        float m_sum[7];
        int   m_head;
        int   m_count;

    public:
        ResidualCost();

        /** @brief push one sample's residual, returns current windowed J */
        float push(const float *resQ, const float *resW, const float *sigma);

        int count() const { return m_count; }   // < W means window not full yet
    };
}

#endif /* FDI_H */