#ifndef RELU_H
#define RELU_H

#include <vector>

class ReLULayer {
public:
    std::vector<float> forward(const std::vector<float>& inputData);
};

#endif 