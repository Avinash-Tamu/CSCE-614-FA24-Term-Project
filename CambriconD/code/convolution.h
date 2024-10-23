#ifndef CONVOLUTION_H
#define CONVOLUTION_H

#include <vector>

class ConvolutionLayer {
public:
    std::vector<float> forward(const std::vector<float>& inputData, const std::vector<float>& weights);
};

#endif // CONVOLUTION_H