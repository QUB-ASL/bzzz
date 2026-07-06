#pragma once

#include <array>

namespace bzzz
{

constexpr int NUM_HYPOTHESES = 7;

class BayesianUpdater
{
public:

    BayesianUpdater();

    void update(const std::array<float, NUM_HYPOTHESES>& likelihood);

    const std::array<float, NUM_HYPOTHESES>& posterior() const;

private:

    std::array<float, NUM_HYPOTHESES> m_prior;
    std::array<float, NUM_HYPOTHESES> m_posterior;
};

}