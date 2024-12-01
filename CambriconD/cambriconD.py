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
    
    # Initialize counters
    total_main_iterations = 0
    total_output_channel_iterations = 0
    total_quantization_operations = 0
    total_multiplier_operations = 0
    total_tile_iterations = 0
    
    # 128x128 PE array (assuming it can handle 128x128 multiplications simultaneously)
    PE_array_size = 128 * 128  # 128x128 array of Processing Elements
    
    for d1 in range(N * Hout * Wout):  # Loop over all output spatial locations
        total_main_iterations += 1  # Count main loop iterations
        
        batch_idx = d1 // (Hout * Wout)
        spatial_idx = d1 % (Hout * Wout)
        out_h = spatial_idx // Wout
        out_w = spatial_idx % Wout
        
        # Step 1: Extract the relevant region of the input (this is like reading a tile)
        input_tile = input_activations[batch_idx, out_h:out_h+Kh, out_w:out_w+Kw, :]
        
        # Step 2: For each output channel (d2), compute the dot product of the input and weight vectors
        for d2 in range(Cout):  # Loop over output channels (Cout)
            total_output_channel_iterations += 1  # Count output channel iterations
            
            # Prepare the weights for the current channel (d2)
            weights_for_d2 = weight_vector[d2, :, :, :]
            
            # Flatten input tile and weights for dot product calculation
            flattened_input = input_tile.flatten()
            flattened_weights = weights_for_d2.flatten()
            
            # Step 3: Quantize the activations and detect outliers
            quantized_activations, overflow_flags = quantize_activations(flattened_input, quantization_threshold)
            total_quantization_operations += len(flattened_input)  # Count quantization operations
            
            # Step 4: Perform the PE computation (dot product) for the current tile
            for _ in range(iterations_per_tile):
                total_tile_iterations += 1  # Count iterations per tile
                total_multiplier_operations += len(flattened_input)  # Count multiplier operations
                multiplier_group(quantized_activations, flattened_weights, overflow_flags, m)
    
    # Print iteration counts
    print(f"Total main iterations (over spatial locations): {total_main_iterations}")
    print(f"Total output channel iterations: {total_output_channel_iterations}")
    print(f"Total quantization operations: {total_quantization_operations}")
    print(f"Total multiplier operations: {total_multiplier_operations}")
    print(f"Total iterations per tile: {total_tile_iterations}")
    
    return output

# Define GUID 128 and GUID 512 parameters
models = {
    "GUID 128": {"Hout": 64, "Wout": 64, "Cout": 128},
    "GUID 512": {"Hout": 128, "Wout": 128, "Cout": 512},
}



#GUID Simulation Prototype

# Common parameters
N = 1  # Batch size
Cin = 3  # Input channels
Kh, Kw = 3, 3  # Kernel size
quantization_threshold = 0.5  # Threshold for outlier detection
m = 1  # Number of outliers that can be handled with fp-fp multipliers

# Iterate through models
for model_name, params in models.items():
    Hout, Wout, Cout = params["Hout"], params["Wout"], params["Cout"]
    
    # Generate input activations and weights
    input_activations = np.random.rand(N, Hout, Wout, Cin)  # Random activations
    weight_vector = np.random.rand(Cout, Kh, Kw, Cin)  # Random weights
    
    # Run the computation
    print(f"\nRunning convolution for {model_name}...")
    output = compute_conv2d_pe(input_activations, weight_vector, (Kh, Kw), quantization_threshold, m)




# Uncomment the below code and comment the above code ("#GUID Simulation Prototype" onwards) for sample model simulation with custom weights and I/O channels

# # Example input activations and weights (simulating a batch of inputs)
# N, Hout, Wout, Cin = 1, 128, 128, 3  # 1 sample, 128x128 output, 3 input channels (for large output)
# Kh, Kw = 3, 3  # Kernel size (3x3)
# Cout = 64  # Number of output channels (for example, 64 output channels)

# # Example input and weight buffers
# input_activations = np.random.rand(N, Hout, Wout, Cin)  # Simulate random input activations
# weight_vector = np.random.rand(Cout, Kh, Kw, Cin)  # Simulate random weights for 64 output channels

# # Set the quantization threshold for outlier detection and number of outlier handling multipliers
# quantization_threshold = 0.5  # Threshold for considering an activation as an outlier
# m = 1  # Number of outliers that can be handled with fp-fp multipliers

# # Perform the convolution computation
# output = compute_conv2d_pe(input_activations, weight_vector, (Kh, Kw), quantization_threshold, m)

# Output the result (this won't print output as we are focusing on the iteration counts)
# print("Convolution result:")
# print(output)
