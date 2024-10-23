#include "convolution.h"
#include "relu.h"

int main() {
    ConvolutionLayer convLayer;
    ReLULayer reluLayer;

    // Dummy data initialization
    std::vector<float> inputData = { /* ... */ };
    std::vector<float> weights = { /* ... */ };

    // Perform operations
    auto output = convLayer.forward(inputData, weights);
    output = reluLayer.forward(output);

    std::cout << "Output: ";
    for (auto val : output) {
        std::cout << val << " ";
    }
    std::cout << std::endl;

    return 0;
}