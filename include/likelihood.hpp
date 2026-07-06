#pragma once

#include <cmath>

namespace bzzz
{

class LikelihoodCalculator
{
public:

    explicit LikelihoodCalculator(float sigma = 1.0f);

    float compute(float residualCost) const;

private:

    float sigmaSquared;
};

}
