class CambriconD:
    def __init__(self):
        self.DRAM = {'weights': [], 'sign_bits': []}
        self.WeightBuffer = {'data': [], 'size': 32 * 1024 * 1024}  # 32 MB
        self.InputBuffer = {'data': [], 'size': 64 * 1024 * 1024}   # 64 MB
        self.OutputBuffer = {'data': [], 'size': 64 * 1024 * 1024}  # 64 MB
        self.PE_Array = []
        self.SFU = {'input': [], 'output': []}
        self.CompressionUnit = {'increments': [], 'compressed': []}
        
    def load_weights(self, weights):
        """Load weights from DRAM to Weight Buffer"""
        if len(weights) <= self.WeightBuffer['size']:
            self.DRAM['weights'] = weights
            print("Loaded weights into DRAM")
        
    def load_input(self, inputs):
        """Load inputs from DRAM to Input Buffer"""
        if len(inputs) <= self.InputBuffer['size']:
            self.InputBuffer['data'] = inputs
            print("Loaded inputs into Input Buffer")

    def process_data_in_pe(self):
        """Process data in the PE Array with weights and input values"""
        # Step 1: Load weights from DRAM to Weight Buffer
        self.WeightBuffer['data'] = self.DRAM['weights']
        
        # Step 2: Move inputs from SFU to PE Array
        self.PE_Array = self.InputBuffer['data']
        
        # Processing in PE Array
        processed_data = [weight * input_data for weight, input_data in zip(self.WeightBuffer['data'], self.PE_Array)]
        print("Processed data in PE Array")
        
        # Step 3: Send output to Output Buffer for ReLU computation
        self.OutputBuffer['data'] = processed_data

    def relu_computation(self):
        """Perform ReLU computation on data in Output Buffer using SFU"""
        # Step 4: Fetch sign bits from DRAM to SFU
        self.SFU['input'] = self.DRAM['sign_bits']
        
        # ReLU computation (simplified)
        relu_output = [max(0, x) for x in self.OutputBuffer['data']]
        self.SFU['output'] = relu_output
        print("Completed ReLU computation")

    def compression(self):
        """Perform compression on raw activation values"""
        # Step 5: Increment values sent to Compression Unit
        increments = [x + 1 for x in self.SFU['output']]  # Increment each activation
        self.CompressionUnit['increments'] = increments
        print("Increments computed and sent to Compression Unit")
        
        # Step 6: Compress the increments
        self.CompressionUnit['compressed'] = self.compress_data(increments)
        print("Data compressed in Compression Unit")

    def compress_data(self, data):
        """Simulate data compression (simple example)"""
        # A placeholder compression function (e.g., run-length encoding, etc.)
        compressed_data = [x // 2 for x in data]  # Simple compression simulation
        return compressed_data

# Instantiate and run simulation
architecture = CambriconD()

# Simulating data inputs
weights = [2, 3, 5, 7]  # Example weights
inputs = [1, 1, 1, 1]   # Example inputs
sign_bits = [1, 0, 1, 0]

# Load data into the architecture
architecture.load_weights(weights)
architecture.DRAM['sign_bits'] = sign_bits
architecture.load_input(inputs)

# Simulate dataflow
architecture.process_data_in_pe()
architecture.relu_computation()
architecture.compression()

# Display results
print("Final compressed data:", architecture.CompressionUnit['compressed'])