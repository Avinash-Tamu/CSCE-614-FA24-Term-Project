import math
import numpy as np
from tqdm import tqdm

class scale_config:
    def __init__(self):
        self.array_rows = 10  # Number of rows in the systolic array
        self.array_cols = 10  # Number of columns in the systolic array
        self.quantization_threshold = 0.5  # Threshold for quantization
        self.num_multiplier_fpfp = 1  # Number of FP-FP multipliers

    def get_array_dims(self):
        return (self.array_rows, self.array_cols)

class systolic_compute_os:
    def __init__(self, config):
        self.config = config

        self.arr_row, self.arr_col = 10,10#self.config.get_array_dims()
        self.quantization_threshold = 0.5#self.config.quantization_threshold
        self.num_multiplier_fpfp = 1#self.config.num_multiplier_fpfp

        # Initialize matrices based on the array dimensions
        self.ifmap_op_mat = np.random.rand(self.arr_row, self.arr_col)
        self.ofmap_op_mat = np.zeros((self.arr_row, self.arr_col, 3))  # Assuming 3 output channels
        self.filter_op_mat = np.random.rand(3, self.arr_row, self.arr_col)  # Adjust based on your model

        # Derived parameters
        self.Sr = self.ifmap_op_mat.shape[0]
        self.Sc = self.filter_op_mat.shape[1]  # Assuming filter shape matches output channels
        self.T = self.ifmap_op_mat.shape[1]

        self.row_fold = math.ceil(self.Sr / self.arr_row)
        self.col_fold = math.ceil(self.Sc / self.arr_col)

        # Generated matrices
        self.ifmap_prefetch_matrix = np.zeros((1, 1))
        self.filter_prefetch_matrix = np.zeros((1, 1))

        # Flags
        self.params_set_flag = True
        self.prefetch_mat_ready_flag = False

    def set_params(self, ifmap_op_mat=None, ofmap_op_mat=None, filter_op_mat=None):
        # Check if matrices are provided and set them
        if ifmap_op_mat is not None:
            self.ifmap_op_mat = ifmap_op_mat
        if ofmap_op_mat is not None:
            self.ofmap_op_mat = ofmap_op_mat
        if filter_op_mat is not None:
            self.filter_op_mat = filter_op_mat

        # Assume dimensions are derived from these matrices
        self.Sr = self.ifmap_op_mat.shape[0]
        self.Sc = self.filter_op_mat.shape[1]
        self.T = self.ifmap_op_mat.shape[1]
        self.arr_row, self.arr_col = self.config.get_array_dims()

        # Other initializations based on new parameters
        self.prepare_matrices()

    def quantize_activations(self, activations):
        quantized_activations = []
        overflow_flags = []
        for activation in activations:
            if abs(activation) > self.quantization_threshold:
                quantized_activations.append(activation)  # Keep as floating point
                overflow_flags.append(True)
            else:
                quantized_activations.append(int(activation))  # Quantize to integer
                overflow_flags.append(False)
        return np.array(quantized_activations), overflow_flags

    def multiplier_group(self, quantized_activations, weights, overflow_flags):
        result = 0
        outlier_count = 0
        for i in range(min(len(quantized_activations), len(weights))):  # Ensure no out-of-bounds error
            if not overflow_flags[i]:
                result += quantized_activations[i] * weights[i]
            else:
                if outlier_count < self.num_multiplier_fpfp:
                    result += quantized_activations[i] * weights[i]
                    outlier_count += 1
                else:
                    max_val = 2**31 - 1
                    min_val = -2**31
                    result += (max_val if quantized_activations[i] > 0 else min_val) * weights[i]
        return result

    def compute_conv2d(self):
        if not self.params_set_flag:
            raise Exception("Parameters not set")
        if not self.prefetch_mat_ready_flag:
            self.create_prefetch_matrices()

        Hout, Wout, Cout = self.ofmap_op_mat.shape[0], self.ofmap_op_mat.shape[1], self.filter_op_mat.shape[0]
        output = np.zeros((Hout, Wout, Cout))
        for d1 in range(Hout * Wout):
            out_h = d1 // Wout
            out_w = d1 % Wout
            for d2 in range(Cout):
                if d2 >= self.filter_prefetch_matrix.shape[0]:
                    continue  # Skip if the index exceeds the available filter matrices
                input_tile = self.ifmap_prefetch_matrix[:, d1].flatten() if d1 < self.ifmap_prefetch_matrix.shape[1] else np.zeros_like(self.ifmap_op_mat.flatten())
                weights_for_d2 = self.filter_prefetch_matrix[d2, :].flatten()
                quantized_activations, overflow_flags = self.quantize_activations(input_tile)
                result = self.multiplier_group(quantized_activations, weights_for_d2, overflow_flags)
                output[out_h, out_w, d2] = result
        return output

    def create_prefetch_matrices(self):
        # Placeholder for actual matrix creation logic
        self.prefetch_mat_ready_flag = True

# Example usage
config = scale_config()
scos = systolic_compute_os(config)
output = scos.compute_conv2d()
print(output)
