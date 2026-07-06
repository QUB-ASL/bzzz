#include "fdi.hpp"

namespace bzzz
{

ModelBasedBayesianFDI::ModelBasedBayesianFDI()
:
likelihoodCalculator(FDI_RESIDUAL_SIGMA),
m_faultDetected(false),
m_failedMotor(0),
m_confidence(1.0f),
m_lastResidualCost(0.0f),
m_lastWindowCost(0.0f)
{
}

void ModelBasedBayesianFDI::update(
    const VehicleState& measuredState,
    const float motorCommand[6])
{

    ActuatorHealth hypotheses[NUM_HYPOTHESES];

    std::array<float, NUM_HYPOTHESES> likelihoods;

    float windowCosts[NUM_HYPOTHESES];

    //--------------------------------------------------
    // Fault hypotheses
    //--------------------------------------------------

    hypotheses[1].gamma[0] = 0.0f;
    hypotheses[2].gamma[1] = 0.0f;
    hypotheses[3].gamma[2] = 0.0f;
    hypotheses[4].gamma[3] = 0.0f;
    hypotheses[5].gamma[4] = 0.0f;
    hypotheses[6].gamma[5] = 0.0f;

    for(int h=0; h<NUM_HYPOTHESES; h++)
    {
        VehicleState predictedState =
            predictor.predict(
                measuredState,
                motorCommand,
                hypotheses[h],
                FDI_SAMPLING_TIME);

        Residual residual =
            residualGenerator.compute(
                measuredState,
                predictedState);

        float residualCostValue =
            residualCost.compute(residual);

        windowCosts[h] =
            slidingWindows[h].update(residualCostValue);

        likelihoods[h] =
            likelihoodCalculator.compute(windowCosts[h]);

        // Save healthy-model values
        if(h==0)
        {
            m_lastResidualCost = residualCostValue;
            m_lastWindowCost   = windowCosts[h];
        }
    }

    bayesianUpdater.update(likelihoods);

    const auto& posterior =
        bayesianUpdater.posterior();

    m_lastPosterior = posterior;

    m_failedMotor =
        mapDecision.decide(posterior);

    m_confidence =
        posterior[m_failedMotor];

    if(m_failedMotor != 0 &&
       m_confidence > FDI_CONFIDENCE_THRESHOLD)
    {
        m_faultDetected = true;
    }
    else
    {
        m_faultDetected = false;
    }
}

bool ModelBasedBayesianFDI::faultDetected() const
{
    return m_faultDetected;
}

int ModelBasedBayesianFDI::failedMotor() const
{
    return m_failedMotor;
}

float ModelBasedBayesianFDI::confidence() const
{
    return m_confidence;
}

float ModelBasedBayesianFDI::latestResidualCost() const
{
    return m_lastResidualCost;
}

float ModelBasedBayesianFDI::latestWindowCost() const
{
    return m_lastWindowCost;
}

const std::array<float, NUM_HYPOTHESES>&
ModelBasedBayesianFDI::latestPosterior() const
{
    return m_lastPosterior;
}

}