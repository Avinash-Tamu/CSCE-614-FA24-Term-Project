

# Cambricon-D Implementation

This project implements a simplified version of Cambricon-D focusing on convolution and ReLU operators. Cambricon-D is a full-network differential computing architecture designed to accelerate diffusion models by reducing memory access overheads.

## Project Structure

- `main.cpp`: The main entry point for the application. Initializes components and runs the main processing loop.
- `convolution.h` / `convolution.cpp`: Implements convolution operations using delta values.
- `relu.h` / `relu.cpp`: Implements ReLU activation using sign-mask dataflow.
- `dataflow.h` / `dataflow.cpp`: Manages dataflow and memory access.
- `pe_array.h` / `pe_array.cpp`: Simulates the Processing Element (PE) array design.
- `simulator.h` / `simulator.cpp`: Simulates or analytically models performance metrics.
- `config.h`: Stores configuration settings for models and hardware.
- `Makefile`: Automates the build process.

**Implementation Steps**

1. Focus on Convolution and ReLU
    **Convolution**: Implement the convolution operations by focusing on delta values ($\Delta X_t$) rather than raw input values ($X_t$). This involves computing convolutions using the differences between consecutive timesteps, which are typically smaller and can be represented with lower precision, such as INT3 instead of FP16.
    
    **ReLU Activation**: Use the sign-mask dataflow for ReLU operations. This involves approximating the ReLU function using only the sign bits of the previous timestep's output. The ReLU function is defined as:
        -> ReLU(Yt) = Yt .sgn(Yt)
        For differential computing, approximate:
        -> Delta Yt’ = delta Yt.sgn(Yt-1)

    This approximation allows the use of 1-bit sign information instead of full-width raw inputs, significantly reducing memory access overhead
2. Sign-Mask Dataflow
    -> Implement a dataflow where only the sign bits of activations are fetched from memory, reducing the need to load full precision activations. This is crucial for maintaining efficiency in differential computing across layers.
    -> The sign-mask dataflow consists of:
        -> Loading weights onto on-chip buffers.
        -> Performing tensor multiplications using delta activations ($\Delta X_t$).
        -> Fetching sign bits from off-chip memory to use in ReLU computations.
        -> Computing ReLU on delta values using these sign bits

3. Processing Element (PE) Array Design
    -> Design the PE array to handle both inlier and outlier computations efficiently:
        -> Use INT3 for most computations (inliers) and FP16 for outliers.
        -> Implement a mechanism to handle outliers separately without significant synchronization overhead

4. Simulation and Evaluation
    -> Since specific simulators for diffusion models might not exist, consider using general-purpose simulators like **ScaleSim** or create an analytical model to estimate performance metrics like cycle counts, memory access patterns, and speedup.
    -> Regenerate results focusing on metrics such as average memory access and speedup, comparing them against baseline implementations
