#pragma once

#include "residual.hpp"

namespace bzzz
{

class ResidualCost
{
public:

    float compute(const Residual& r);

};

}