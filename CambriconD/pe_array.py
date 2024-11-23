import numpy as np

# Define convolution parameters
N, H_in, W_in, C_in = 1, 5, 5, 3  # Batch size, input height, input width, input channels
K, C_out = 3, 2  # Kernel size (KxK), number of output channels
H_out, W_out = 3, 3  # Output height, output width

# Input and weights (random initialization)
InputBuf = np.random.rand(N, H_in, W_in, C_in)  # Shape: (N, H_in, W_in, C_in)
WeightBuf = np.random.rand(K, K, C_in, C_out)  # Shape: (K, K, C_in, C_out)
OutputBuf = np.zeros((N, H_out, W_out, C_out))  # Shape: (N, H_out, W_out, C_out)

# Activation function (ReLU)
def relu(x):
    return np.maximum(0, x)

# Tile reading function (simplified for this example)
def read_tile(array, d1, d3, tile_size):
    # For simplicity, we simulate reading a tile from the array
    # A tile is a subset of the input or weight data
    return array[d1, :tile_size, :tile_size, :]

# Convolution Tile Computation (Dot product computation for the tile)
def compute_tile(input_tile, weight_tile):
    # Perform element-wise multiplication and sum to get the dot product
    return np.sum(input_tile * weight_tile)

# Simulate the parallel 2D Convolution using the PE array
def compute_conv2d(input_buf, weight_buf, output_buf):
    N, H_in, W_in, C_in = input_buf.shape
    K, _, _, C_out = weight_buf.shape
    H_out = W_out = H_in - K + 1  # Assuming stride = 1 and no padding

    # Parallel loops (we'll use regular loops to simulate parallelism)
    for d1 in range(N):  # Loop over batches
        for d2 in range(C_out):  # Loop over output channels
            for d3 in range(K * K * C_in):  # Loop over kernel elements (simplified for this example)
                # Read a tile from InputBuf and WeightBuf for this specific PE
                input_tile = read_tile(input_buf, d1, d3, K)
                weight_tile = read_tile(weight_buf, d2, d3, K)

                # Initialize the output tile with zeros
                tile_out = np.zeros((H_out, W_out))

                # Iterate over the output dimensions (height and width)
                for i in range(H_out):
                    for j in range(W_out):
                        # For each position, compute the dot product for the tile
                        tile_out[i, j] = compute_tile(input_tile[i:i+K, j:j+K, :], weight_tile)

                # Write the tile result to the output buffer
                output_buf[d1, :, :, d2] += tile_out

    # Apply activation function (e.g., ReLU) after the convolution
    output_buf = relu(output_buf)

# Run the simulation
compute_conv2d(InputBuf, WeightBuf, OutputBuf)

# Output the result
print("Output of the convolution (after ReLU):")
print(OutputBuf)

