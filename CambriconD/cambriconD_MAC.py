import numpy as np

def quantize_activations(activations, quantization_threshold=0.5):
    quantized_activations = []
    overflow_flags = []
    for activation in activations:
        if abs(activation) > quantization_threshold:
            quantized_activations.append(activation)  # Keep as floating point
            overflow_flags.append(True)
        else:
            quantized_activations.append(int(activation))  # Quantize to integer
            overflow_flags.append(False)
    return np.array(quantized_activations), overflow_flags

def multiplier_group(quantized_activations, weights, overflow_flags, m, int_max_value=2**31 - 1, int_min_value=-2**31):
    result = 0
    outlier_count = 0
    for i in range(len(quantized_activations)):
        if not overflow_flags[i]:  # Inlier (integer activation)
            result += quantized_activations[i] * weights[i]
        else:  # Outlier (floating-point activation)
            if outlier_count < m:
                result += quantized_activations[i] * weights[i]
                outlier_count += 1
            else:
                result += (int_max_value if quantized_activations[i] > 0 else int_min_value) * weights[i]
    return result

def compute_conv2d_pe(input_activations, weight_vector, kernel_size, quantization_threshold=0.5, m=1, iterations_per_tile=2):
    N, Hout, Wout, Cin = input_activations.shape
    Cout, Kh, Kw, Cin_weight = weight_vector.shape

    if Cin != Cin_weight:
        raise ValueError(f"Input channels ({Cin}) and weight channels ({Cin_weight}) must match.")

    output = np.zeros((Hout, Wout, Cout))

    # Memory access and iteration counters
    activation_memory_accesses = 0
    weight_memory_accesses = 0
    total_main_iterations = 0
    total_output_channel_iterations = 0
    total_quantization_operations = 0
    total_multiplier_operations = 0
    total_tile_iterations = 0

    for d1 in range(N * Hout * Wout):
        total_main_iterations += 1
        batch_idx = d1 // (Hout * Wout)
        spatial_idx = d1 % (Hout * Wout)
        out_h = spatial_idx // Wout
        out_w = spatial_idx % Wout
        
        input_tile = input_activations[batch_idx, out_h:out_h+Kh, out_w:out_w+Kw, :]
        activation_memory_accesses += 1

        for d2 in range(Cout):
            total_output_channel_iterations += 1
            weights_for_d2 = weight_vector[d2, :, :, :]
            weight_memory_accesses += 1

            flattened_input = input_tile.flatten()
            flattened_weights = weights_for_d2.flatten()

            quantized_activations, overflow_flags = quantize_activations(flattened_input, quantization_threshold)
            total_quantization_operations += len(flattened_input)

            for _ in range(iterations_per_tile):
                total_tile_iterations += 1
                total_multiplier_operations += len(flattened_input)
                result = multiplier_group(quantized_activations, flattened_weights, overflow_flags, m)

    # Print iteration and memory access counts
    print(f"Total main iterations (over spatial locations): {total_main_iterations}")
    print(f"Total output channel iterations: {total_output_channel_iterations}")
    print(f"Total quantization operations: {total_quantization_operations}")
    print(f"Total multiplier operations: {total_multiplier_operations}")
    print(f"Total iterations per tile: {total_tile_iterations}")
    print(f"Activation memory accesses: {activation_memory_accesses}")
    print(f"Weight memory accesses: {weight_memory_accesses}")

    return output

# Example usage
N, Hout, Wout, Cin = 1, 128, 128, 3
Kh, Kw = 3, 3
Cout = 64
input_activations = np.random.rand(N, Hout + Kh - 1, Wout + Kw - 1, Cin)  # Extended dimensions for valid convolution
weight_vector = np.random.rand(Cout, Kh, Kw, Cin)
quantization_threshold = 0.5
m = 1
output = compute_conv2d_pe(input_activations, weight_vector, (Kh, Kw), quantization_threshold, m)
