#pragma once

#include "config.hpp"
#include "predictor.hpp"
#include "residual.hpp"
#include "window.hpp"
#include "cost.hpp"
#include "likelihood.hpp"
#include "bayes.hpp"
#include "map.hpp"
#include <array>

namespace bzzz
{

class ModelBasedBayesianFDI
{
public:

    ModelBasedBayesianFDI();

    void update(
        const VehicleState& measuredState,
        const float motorCommand[6]);

    bool faultDetected() const;

    int failedMotor() const;

    float confidence() const;

    /**
     * Latest residual cost (Healthy hypothesis)
     */
    float latestResidualCost() const;

    /**
     * Latest sliding window cost (Healthy hypothesis)
     */
    float latestWindowCost() const;

    /**
     * Latest Bayesian posterior probabilities
     */
    const std::array<float, NUM_HYPOTHESES>& latestPosterior() const;

private:

    //--------------------------------------------------
    // Bayesian FDI modules
    //--------------------------------------------------

    VehiclePredictor predictor;

    ResidualGenerator residualGenerator;

    std::array<SlidingWindow, NUM_HYPOTHESES> slidingWindows;

    ResidualCost residualCost;

    LikelihoodCalculator likelihoodCalculator;

    BayesianUpdater bayesianUpdater;

    MAPDecision mapDecision;

    //--------------------------------------------------
    // Internal estimator state
    //--------------------------------------------------

    bool m_faultDetected;

    int m_failedMotor;

    float m_confidence;

    float m_lastResidualCost;

    float m_lastWindowCost;

    std::array<float, NUM_HYPOTHESES> m_lastPosterior;
};

}