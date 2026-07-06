#pragma once

#include <array>
#include "bayes.hpp"

namespace bzzz
{

class MAPDecision
{
public:

    int decide(const std::array<float,NUM_HYPOTHESES>& posterior) const;
};

}