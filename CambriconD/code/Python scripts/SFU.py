import numpy as np

# Define constants
INT_MAX = 2147483647  # Define INT_MAX for 32-bit integer
INT_MIN = -2147483648  # Define INT_MIN for 32-bit integer
INPUT_SIZE = 128

# Inputs
sign_bits = np.random.choice([0, 1], INPUT_SIZE)  # Random 0/1 values for sign bits
delta_input = np.random.uniform(-10, 10, INPUT_SIZE)  # Random real values for delta_input
quantized_inliers = np.random.randint(INT_MIN, INT_MAX, INPUT_SIZE)  # Random integer inliers
outlier_bitmap = np.random.choice([0, 1], INPUT_SIZE)  # Random 0/1 values for outlier_bitmap

# Outputs
updated_values = np.zeros(INPUT_SIZE)  # To store the final results
overflow_flags = np.zeros(INPUT_SIZE, dtype=bool)  # Flags for overflow

# Internal variables
decompressed_inliers = np.zeros(INPUT_SIZE)  # Stores decompressed inliers
decompressed_outliers = np.zeros(INPUT_SIZE)  # Stores decompressed outliers
relu_output = np.zeros(INPUT_SIZE)  # Stores ReLU output


def int2fp_conversion(quantized_in, overflow_flags):
    """
    Converts integer quantized values to floating-point values.
    """
    decompressed_out = np.zeros(INPUT_SIZE)
    for i in range(INPUT_SIZE):
        if quantized_in[i] == INT_MIN:
            decompressed_out[i] = 0.0  # Map INT_MIN to 0
            overflow_flags[i] = True
        else:
            decompressed_out[i] = float(quantized_in[i])  # Convert to floating-point
            overflow_flags[i] = False
    return decompressed_out


def decompress_outliers(bitmap, delta_in):
    """
    Decompress outliers using the bitmap and delta input.
    """
    outlier_out = np.zeros(INPUT_SIZE)
    for i in range(INPUT_SIZE):
        if bitmap[i]:
            outlier_out[i] = delta_in[i]
        else:
            outlier_out[i] = 0.0
    return outlier_out


def relu_func(sign_bits, delta_in):
    """
    Applies the ReLU function to delta_input using sign_bits.
    """
    relu_out = np.zeros(INPUT_SIZE)
    for i in range(INPUT_SIZE):
        if sign_bits[i]:
            relu_out[i] = delta_in[i]  # Keep the value
        else:
            relu_out[i] = 0.0  # Set to 0
    return relu_out


# Main execution
# Step 1: Convert integers to floating-point
decompressed_inliers = int2fp_conversion(quantized_inliers, overflow_flags)

# Step 2: Decompress outliers
decompressed_outliers = decompress_outliers(outlier_bitmap, delta_input)

# Step 3: Apply the ReLU function
relu_output = relu_func(sign_bits, delta_input)

# Combine outputs (if necessary)
updated_values = decompressed_inliers + decompressed_outliers + relu_output

# Display results
print("Decompressed Inliers:", decompressed_inliers)
print("Decompressed Outliers:", decompressed_outliers)
print("ReLU Output:", relu_output)
print("Updated Values:", updated_values)
print("Overflow Flags:", overflow_flags)