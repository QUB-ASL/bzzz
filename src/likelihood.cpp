#include "likelihood.hpp"

namespace bzzz
{

LikelihoodCalculator::LikelihoodCalculator(float sigma)
{
    sigmaSquared = sigma * sigma;
}

float LikelihoodCalculator::compute(float residualCost) const
{
    return std::exp(-residualCost / (2.0f * sigmaSquared));
}

}