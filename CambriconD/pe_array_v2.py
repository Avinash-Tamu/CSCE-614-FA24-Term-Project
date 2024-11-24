import numpy as np

# Simulate the quantization of input activations
def quantize_activations(activations, quantization_threshold=0.5):
    """
    Quantize the input activations. Activations that overflow the threshold
    will be marked as outliers.
    """
    quantized_activations = []
    overflow_flags = []
    for activation in activations:
        if abs(activation) > quantization_threshold:  # outlier
            quantized_activations.append(activation)  # Keep as FP
            overflow_flags.append(True)
        else:  # inlier
            quantized_activations.append(int(activation))  # Quantize to int
            overflow_flags.append(False)
    
    return np.array(quantized_activations), overflow_flags

# Simulate the PE multiplier group: Inliers are handled with int-fp multipliers, outliers with fp-fp multipliers
def multiplier_group(quantized_activations, weights, overflow_flags, m, int_max_value=2*31 - 1, int_min_value=-2*31):
    """
    Simulate the multiplier group behavior with both int-fp and fp-fp multipliers.
    """
    result = 0
    outlier_count = 0
    inlier_count = 0
    
    for i in range(len(quantized_activations)):
        if not overflow_flags[i]:  # inlier (int activation)
            # Multiply the quantized activation (int) with the weight (fp)
            result += quantized_activations[i] * weights[i]
            inlier_count += 1
        else:  # outlier (fp activation)
            if outlier_count < m:  # Handle outliers with fp-fp multipliers
                result += quantized_activations[i] * weights[i]  # Use the original FP activation
                outlier_count += 1
            else:  # If more outliers than m, replace with INT_MAX/INT_MIN
                result += (int_max_value if quantized_activations[i] > 0 else int_min_value) * weights[i]
    
    return result

# Simulate the 2D Convolution with a PE array
def compute_conv2d_pe(input_activations, weight_vector, kernel_size, quantization_threshold=0.5, m=1, iterations_per_tile=2):
    """
    Simulates the 2D convolution with a PE group, quantization, overflow detection,
    and handling of inliers and outliers in the multiplier group.
    """
    N, Hout, Wout, Cin = input_activations.shape  # Here, input_activations should be a 4D array
    Cout, Kh, Kw, Cin_weight = weight_vector.shape  # Correct unpacking for 4D weight vector
    
    # Ensure that Cin of input and weight are the same
    if Cin != Cin_weight:
        raise ValueError(f"Input channels ({Cin}) and weight channels ({Cin_weight}) must match.")
    
    output = np.zeros((Hout, Wout, Cout))  # Output with Cout channels
    
    for d1 in range(N * Hout * Wout):  # Loop over all output spatial locations
        batch_idx = d1 // (Hout * Wout)
        spatial_idx = d1 % (Hout * Wout)
        out_h = spatial_idx // Wout
        out_w = spatial_idx % Wout
        
        # Step 1: Extract the relevant region of the input (this is like reading a tile)
        input_tile = input_activations[batch_idx, out_h:out_h+Kh, out_w:out_w+Kw, :]
        
        # Step 2: For each output channel (d2), compute the dot product of the input and weight vectors
        for d2 in range(Cout):  # Loop over output channels (Cout)
            # Prepare the weights for the current channel (d2)
            weights_for_d2 = weight_vector[d2, :, :, :]
            
            # Flatten input tile and weights for dot product calculation
            flattened_input = input_tile.flatten()
            flattened_weights = weights_for_d2.flatten()
            
            # Step 3: Quantize the activations and detect outliers
            quantized_activations, overflow_flags = quantize_activations(flattened_input, quantization_threshold)
            
            # Step 4: Perform the PE computation (dot product) for the current tile
            result = 0
            for _ in range(iterations_per_tile):
                result += multiplier_group(quantized_activations, flattened_weights, overflow_flags, m)
            
            # Step 5: Store the result in the output buffer
            output[out_h, out_w, d2] = result
    
    return output

# Example input activations and weights (simulating a batch of inputs)
N, Hout, Wout, Cin = 1, 2, 2, 3  # 1 sample, 2x2 output, 3 input channels
Kh, Kw = 3, 3  # Kernel size (3x3)
Cout = 2  # Number of output channels

# Example input and weight buffers
input_activations = np.array([[[[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]],
                               [[0.3, 0.4, 0.5], [0.4, 0.5, 0.6]]],  # First 2x2 section
                              [[[0.5, 0.6, 0.7], [0.6, 0.7, 0.8]],
                               [[0.7, 0.8, 0.9], [0.8, 0.9, 1.0]]]]) # Second 2x2 section

weight_vector = np.array([[[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
                           [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
                           [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]],  # First output channel

                          [[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
                           [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
                           [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]]])  # Second output channel

# Set the quantization threshold for outlier detection and number of outlier handling multipliers
quantization_threshold = 0.5  # Threshold for considering an activation as an outlier
m = 1  # Number of outliers that can be handled with fp-fp multipliers

# Perform the convolution computation
output = compute_conv2d_pe(input_activations, weight_vector, (Kh, Kw), quantization_threshold, m)

# Output the result
print("Convolution result:")
print(output)