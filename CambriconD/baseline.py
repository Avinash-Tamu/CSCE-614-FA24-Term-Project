import numpy as np

# Constants for the baseline system
PE_ARRAY_DIM = 128  # 128x128 PE array
NUM_PES = PE_ARRAY_DIM * PE_ARRAY_DIM  # Total number of PEs in the array (16,384 PEs)
FLOPS_PER_PE = 1  # Each PE performs 1 FLOP per cycle
CLOCK_SPEED_GHZ = 1  # 1 GHz clock
MEMORY_BANDWIDTH_TBPS = 1.5  # 1.5 TB/s memory bandwidth

# Simulation time-related constants
CLOCK_CYCLE_TIME_NS = 1 / CLOCK_SPEED_GHZ  # Time per clock cycle in nanoseconds
MEMORY_BANDWIDTH_BPS = MEMORY_BANDWIDTH_TBPS * 1e12  # Convert TB/s to bytes per second

# Matrix dimensions for operations (for example, 128x128 matrix multiplication)
MATRIX_DIM = 128  # Dimension of input matrices (square for simplicity)
# Input operand matrices (e.g., IFMAP, FILTER, OFMAP)
ifmap = np.random.rand(MATRIX_DIM, MATRIX_DIM)  # Input feature map
filter_matrix = np.random.rand(MATRIX_DIM, MATRIX_DIM)  # Filter matrix
ofmap = np.zeros((MATRIX_DIM, MATRIX_DIM))  # Output feature map (initialized to zeros)

# Class for Systolic Array Simulation
class SystolicArraySimulator:
    def _init_(self):
        # Initialize cycle counters and other metrics
        self.total_cycles = 0  # Initialize total cycles
        self.memory_access_cycles = 0
        self.compute_cycles = 0
        self.memory_access_time = 0

    def compute(self, ifmap, filter_matrix):
        """
        Perform matrix multiplication (simplified version) for systolic array computation.
        Each PE performs one multiply-accumulate operation per cycle.
        """
        # Assume a simple matrix multiplication (for example: ifmap * filter_matrix = ofmap)
        # In a real systolic array, this would be distributed across the PEs in the array.
        
        self.compute_cycles = MATRIX_DIM * MATRIX_DIM  # Each PE does one operation per cycle
        self.total_cycles += self.compute_cycles

        # Simulate compute (multiplying ifmap and filter_matrix)
        for i in range(MATRIX_DIM):
            for j in range(MATRIX_DIM):
                for k in range(MATRIX_DIM):
                    ofmap[i, j] += ifmap[i, k] * filter_matrix[k, j]

        return ofmap

    def memory_access(self):
        """
        Simulate memory access cycles for reading input matrices and writing the output matrix.
        """
        # Calculate memory accesses (read for ifmap and filter_matrix, write for ofmap)
        # For simplicity, let's assume that reading a matrix and writing an output matrix
        # requires the same amount of time per element.
        
        # Memory access cycles (one read per matrix element and one write per output element)
        read_access_cycles = (MATRIX_DIM * MATRIX_DIM * 2)  # ifmap + filter_matrix
        write_access_cycles = MATRIX_DIM * MATRIX_DIM  # ofmap
        
        self.memory_access_cycles = read_access_cycles + write_access_cycles
        self.total_cycles += self.memory_access_cycles
        
        # Memory access time (based on bandwidth)
        memory_access_time = (MATRIX_DIM * MATRIX_DIM * 2 * 8) / MEMORY_BANDWIDTH_BPS  # Convert to bytes
        self.memory_access_time = memory_access_time * 1e9  # Convert to nanoseconds
        return self.memory_access_time
    

    def get_total_cycles(self):
        """
        Return the total number of cycles the simulation ran for.
        """
        return self.total_cycles

    def get_compute_cycles(self):
        """
        Return the total number of cycles spent in computation.
        """
        return self.compute_cycles

    def get_memory_access_cycles(self):
        """
        Return the total number of cycles spent in memory access.
        """
        return self.memory_access_cycles


# Initialize the simulator
simulator = SystolicArraySimulator()

# Perform the computation (matrix multiplication)
simulator.compute(ifmap, filter_matrix)

# Simulate memory access for reading input matrices and writing output matrix
memory_access_time_ns = simulator.memory_access()

# Calculate the total number of cycles for the entire computation
total_cycles = simulator.get_total_cycles()
compute_cycles = simulator.get_compute_cycles()
memory_access_cycles = simulator.get_memory_access_cycles()

# Output results
print(f"Total Cycles for Computation: {compute_cycles}")
print(f"Total Memory Access Cycles: {memory_access_cycles}")
print(f"Total Cycles for Simulation: {total_cycles}")
print(f"Memory Access Time: {memory_access_time_ns:.2f} ns")

# Speedup calculation (example, assuming NVIDIA A100 takes 4 seconds to run)
time_on_simulator = total_cycles * CLOCK_CYCLE_TIME_NS * 1e-9  # Convert to seconds
time_on_a100 = 4  # Example: assume the A100 takes 4 seconds for the same operation
speedup = time_on_a100 / time_on_simulator
print(f"Speedup over NVIDIA A100: {speedup:.2f}x")