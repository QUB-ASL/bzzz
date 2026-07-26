#include "map.hpp"

namespace bzzz
{

int MAPDecision::decide(
    const std::array<float,NUM_HYPOTHESES>& posterior) const
{
    int best = 0;

    float maxValue = posterior[0];

    for(int i=1;i<7;i++)
    {
        if(posterior[i]>maxValue)
        {
            maxValue=posterior[i];
            best=i;
        }
    }
    return best;
}

}