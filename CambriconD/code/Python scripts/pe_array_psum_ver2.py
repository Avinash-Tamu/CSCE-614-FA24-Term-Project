import numpy as np

# Define parameters
PE_ARRAY_SIZE_X = 128
PE_ARRAY_SIZE_Y = 128
INT_MAX = 2147483647      # Define INT_MAX for 32-bit integer(INT3)
INT_MIN = -2147483648     # Define INT_MIN for 32-bit integer(INT3)
INPUT_SIZE = 128
THRESHOLD = 100.0

N = 60
M = 4

# Define input arrays
#A = np.random.rand(INPUT_SIZE) * 500 - 100   # Random values in range [-100, 100]
A = np.zeros(INPUT_SIZE, dtype=np.int64)  # Allocate space with a wider type to handle larger numbers

for i in range(INPUT_SIZE):
    if np.random.rand() > 0.9:  # 10% chance to pick from an extended range
        A[i] = np.random.randint(-8589934592, 8589934591, dtype=np.int64)  # Random int from -2^33 to 2^33-1
    else:
        A[i] = np.random.randint(-2147483648, 2147483647, dtype=np.int64)  # Random int from -2^31 to 2^31-1
     
W = np.random.rand(INPUT_SIZE) * 2 - 1       # Random values in range [-1, 1]
#print("W:",W)

# Outputs
quantized_inliers = np.zeros(INPUT_SIZE, dtype=int)
overflow_flags = np.zeros(INPUT_SIZE, dtype=bool)

inlier_dot_product = np.zeros(INPUT_SIZE, dtype=int)
outlier_dot_product = np.zeros(INPUT_SIZE, dtype=int)
int_dot_product = 0
fp_dot_product = 0


def quantize_activations(A, W):
    quantized_A = np.zeros(INPUT_SIZE, dtype=int)
    overflow_flags = np.zeros(INPUT_SIZE, dtype=bool)
    outlier_count = 0

    for i in range(INPUT_SIZE):
        if (A[i] > INT_MAX) or (A[i]<INT_MIN):
            overflow_flags[i] = True
            outlier_count += 1
        else:
            overflow_flags[i] = False
            quantized_A[i] = int(A[i])

    # If outliers exceed the allowed maximum, set overflowed elements to INT_MAX or INT_MIN
    if outlier_count > M:
        for i in range(INPUT_SIZE):
            if overflow_flags[i]:
                quantized_A[i] = INT_MAX if A[i] > 0 else INT_MIN

    return quantized_A, overflow_flags


def calculate_dot_product(A, quantized_A, W, overflow_flags):
    int_dot_product = 0
    fp_dot_product = 0
    int_multiply = 0
    fp_multiply = 0

    for i in range(INPUT_SIZE):
        if ~overflow_flags[i]:
            fp_dot_product += A[i] * W[i]
            inlier_dot_product[i] = A[i] * W[i]
            fp_multiply += 1
        else:
            int_dot_product += quantized_A[i] * W[i]
            outlier_dot_product[i] = quantized_A[i] * W[i]
            int_multiply += 1

    return int_dot_product, fp_dot_product, int_multiply, fp_multiply


# Simulate PE array operations
def simulate_PE_array(A, W):
    # Quantize activations
    quantized_A, overflow_flags = quantize_activations(A, W)
    
    # Calculate dot product
    int_dot_product, fp_dot_product, int_multiply, fp_multiply = calculate_dot_product(A, quantized_A, W, overflow_flags)
    
    # Output quantized inliers
    quantized_inliers[:] = quantized_A  # Store quantized results in quantized_inliers

    return int_dot_product, fp_dot_product, quantized_inliers, overflow_flags


# Run the simulation
int_dot_product, fp_dot_product, quantized_inliers, overflow_flags = simulate_PE_array(A, W)

# Display results
print("Integer Dot Product:", int_dot_product)
print("Floating-Point Dot Product:", fp_dot_product)
print("Quantized Inliers:", quantized_inliers)
print("Overflow Flags:", overflow_flags)

print("Inlier dot product: ",inlier_dot_product)
print("Outlier dot product: ",outlier_dot_product)
psum = inlier_dot_product+ outlier_dot_product
print("Psum:")
print(psum)
#print("Psum: ",)

