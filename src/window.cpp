#include "config.hpp"
#include "window.hpp"

namespace bzzz
{

SlidingWindow::SlidingWindow()
    : maxSize(FDI_WINDOW_SIZE),
      runningSum(0.0f)
{
}

float SlidingWindow::update(float sample)
{
    history.push_back(sample);

    runningSum += sample;

    if(history.size() > maxSize)
    {
        runningSum -= history.front();
        history.pop_front();
    }

    return runningSum;
}

float SlidingWindow::total() const
{
    return runningSum;
}

}