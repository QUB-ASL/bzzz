#pragma once

#include <deque>

namespace bzzz
{

class SlidingWindow
{
public:
     
    SlidingWindow();

    SlidingWindow(size_t windowSize);

    float update(float sample);

    float total() const;

private:

    std::deque<float> history;

    size_t maxSize;

    float runningSum;
};

}