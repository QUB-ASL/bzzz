#include "bayes.hpp"

namespace bzzz
{

BayesianUpdater::BayesianUpdater()
{
    // Initial belief

    m_prior[0] = 0.99f;

    for(int i=1;i<NUM_HYPOTHESES;i++)
        m_prior[i]=0.01f/6.0f;

    m_posterior = m_prior;
}

void BayesianUpdater::update(
    const std::array<float,NUM_HYPOTHESES>& likelihood)
{
    float sum=0.0f;

    for(int i=0;i<NUM_HYPOTHESES;i++)
    {
        m_posterior[i]
            =
            m_prior[i]
            *
            likelihood[i];

        sum += m_posterior[i];
    }

    if(sum>0.0f)
    {
        for(int i=0;i<NUM_HYPOTHESES;i++)
            m_posterior[i]/=sum;
    }

    // Recursive Bayesian update

    m_prior = m_posterior;
}

const std::array<float,NUM_HYPOTHESES>&
BayesianUpdater::posterior() const
{
    return m_posterior;
}

}