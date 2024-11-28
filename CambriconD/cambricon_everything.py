import numpy as np

class CambriconDSimulator:
    def __init__(self, N, Hout, Wout, Cin, Cout, Kh, Kw, m, n, clock_speed, memory_bandwidth):
        # Architecture parameters
        self.N = N  # Batch size
        self.Hout = Hout  # Output height
        self.Wout = Wout  # Output width
        self.Cin = Cin  # Input channels
        self.Cout = Cout  # Output channels
        self.Kh = Kh  # Kernel height
        self.Kw = Kw  # Kernel width
        self.m = m  # Number of fp-and-fp16 multipliers for outliers
        self.n = n  # Number of int3-and-fp16 multipliers for inliers
        self.clock_speed = clock_speed  # Clock speed (Hz)
        self.memory_bandwidth = memory_bandwidth  # Memory bandwidth (bytes per second)
        
        # PE array size (128x128)
        self.PE_rows = 128
        self.PE_cols = 128
        self.total_PEs = self.PE_rows * self.PE_cols
        
        # Initialize buffers with random values for simulation
        self.InputBuf = np.random.randint(0, 256, (N, Hout, Wout, Cin), dtype=np.uint8)
        self.WeightBuf = np.random.randint(0, 256, (Kh, Kw, Cin, Cout), dtype=np.uint8)
        self.OutputBuf = np.zeros((N, Hout, Wout, Cout), dtype=np.uint16)
        
        # Initialize cycle counters and memory accesses
        self.total_cycles = 0
        self.memory_accesses = 0
    
    def quantize_input(self, input_val):
        """Quantizes input values (simulating fp to int conversion)."""
        int_val = np.clip(input_val, 0, 255)  # Example: scale to 8-bit range
        overflow_flag = 1 if input_val > 255 else 0
        return int_val, overflow_flag
    
    def handle_outliers(self, input_val, overflow_flag):
        """Handles outliers using fp16 multipliers if quantization fails."""
        if overflow_flag:
            return float(input_val)  # Treat as fp16 for outliers
        return input_val  # Inliers are returned as integer
    
    def compute_dot_product(self, input_tile, weight_tile):
        """Computes the dot product of input and weight tiles."""
        return np.sum(input_tile * weight_tile)

    def compute_tile(self, Tilein, Tilew):
        """Simulates the computation of a tile."""
        # Step 1: Quantize the input values
        int_input, overflow_flag = self.quantize_input(Tilein)
        
        # Step 2: Handle inliers and outliers separately
        dot_product = 0
        for i in range(len(int_input)):
            dot_product += self.handle_outliers(int_input[i], overflow_flag[i]) * Tilew[i]
        
        return dot_product

    def compute_conv2d(self):
        """Performs the convolution operation."""
        for d1 in range(self.N * self.Hout * self.Wout // self.PE_rows):
            for d2 in range(self.Cout // self.PE_cols):
                for d3 in range(self.Kh * self.Kw * self.Cin // self.PE_cols):
                    
                    # Step 2: Read tiles from InputBuf and WeightBuf
                    Tilein = self.InputBuf[d1:d1+self.PE_rows, d3:d3+self.PE_cols]
                    Tilew = self.WeightBuf[d2:d2+self.PE_cols, d3:d3+self.PE_cols]
                    
                    # Initialize output tile (zeros initially)
                    Tileout = np.zeros_like(Tilein, dtype=np.uint16)
                    
                    # Step 3: Perform iterations per tile (multiple iterations per tile)
                    for _ in range(self.total_PEs):
                        Tilepartial = self.compute_tile(Tilein, Tilew)
                        Tileout += Tilepartial
                    
                    # Step 4: Write output tile to OutputBuf
                    self.OutputBuf[d1, d2] = Tileout
                    
                    # Step 5: ReLU activation (SFU activation)
                    self.OutputBuf = np.maximum(0, self.OutputBuf)  # ReLU activation
                    
                    # Count memory accesses
                    self.memory_accesses += (self.PE_rows * self.PE_cols)  # Input memory accesses
                    self.memory_accesses += (self.PE_cols * self.PE_cols)  # Weight memory accesses
                    self.memory_accesses += (self.PE_rows * self.PE_cols)  # Output memory accesses

                    # Estimate cycles for memory access and computation:
                    # Each read/write operation takes some cycles (simplified)
                    # Memory accesses: Reading InputBuf, WeightBuf, and Writing OutputBuf
                    memory_access_cycles = (self.PE_rows * self.PE_cols * 2)  # Read input and weight
                    memory_access_cycles += (self.PE_rows * self.PE_cols)  # Write to OutputBuf
                    
                    # Each computation involves dot product calculation (for simplicity, count as 1 cycle)
                    computation_cycles = self.PE_cols * self.PE_cols  # One cycle per operation
                    
                    # Add memory and computation cycles
                    self.total_cycles += memory_access_cycles + computation_cycles

    def get_total_cycles(self):
        return self.total_cycles

    def get_memory_accesses(self):
        return self.memory_accesses


# Initialize the simulation
simulator = CambriconDSimulator(
    N=32, Hout=64, Wout=64, Cin=3, Cout=64, Kh=3, Kw=3, 
    m=60, n=4, clock_speed=1e9, memory_bandwidth=1.5e12
)

# Run the convolution simulation
simulator.compute_conv2d()

# Output the simulation results
print(f"Total Cycles: {simulator.get_total_cycles()}")
print(f"Total Memory Accesses: {simulator.get_memory_accesses()}")