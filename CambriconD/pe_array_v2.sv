module conv2d_pe #(
    // Default parameter values that can be overridden during instantiation
    parameter int N = 8,           // Number of input batches
    parameter int Hout = 32,       // Output height
    parameter int Wout = 32,       // Output width
    parameter int Cin = 3,         // Number of input channels
    parameter int Cout = 16,       // Number of output channels
    parameter int Kh = 3,          // Kernel height
    parameter int Kw = 3           // Kernel width
)(
    input logic clk,
    input logic reset,
    input logic [31:0] input_activations [0:N-1][0:Hout-1][0:Wout-1][0:Cin-1],
    input logic [31:0] weights [0:Kh-1][0:Kw-1][0:Cin-1][0:Cout-1],
    input logic [31:0] quantization_threshold,
    input logic [31:0] m,
    output logic [31:0] conv_output [0:Hout-1][0:Wout-1][0:Cout-1]
);

    // Quantized activations and overflow flags
    logic [31:0] quantized_activations [0:Kh*Kw*Cin-1];
    logic overflow_flags [0:Kh*Kw*Cin-1];

    // Intermediate result for dot product
    logic [63:0] result;

    // Declare flattened_weights statically (to persist through simulation)
    logic [31:0] flattened_weights [0:Kh*Kw*Cin-1];

    // Helper task to quantize activations
    task quantize_activations(input logic [31:0] activations [0:Kh*Kw*Cin-1],
                               output logic [31:0] quantized_activations [0:Kh*Kw*Cin-1],
                               output logic overflow_flags [0:Kh*Kw*Cin-1]);
        for (int i = 0; i < Kh*Kw*Cin; i++) begin
            if (activations[i] > quantization_threshold) begin
                quantized_activations[i] = activations[i];  // Keep as FP
                overflow_flags[i] = 1;
            end else begin
                quantized_activations[i] = activations[i];  // Quantize to integer (rounded off)
                overflow_flags[i] = 0;
            end
        end
    endtask

    // Helper task for PE multiplier group simulation
    task multiplier_group(input logic [31:0] quantized_activations [0:Kh*Kw*Cin-1],
                          input logic [31:0] weights [0:Kh*Kw*Cin-1],
                          input logic overflow_flags [0:Kh*Kw*Cin-1],
                          input int m,  // Use int instead of integer
                          output logic [63:0] result);
        static int outlier_count = 0;  // static int instead of integer
        static int inlier_count = 0;   // static int instead of integer
        result = 0;
        for (int i = 0; i < Kh*Kw*Cin; i++) begin
            if (overflow_flags[i] == 0) begin  // inlier (int activation)
                result = result + (quantized_activations[i] * weights[i]);  // Multiply with weights (using integer arithmetic)
                inlier_count = inlier_count + 1;
            end else begin  // outlier (fp activation)
                if (outlier_count < m) begin
                    result = result + (quantized_activations[i] * weights[i]);  // Use the original FP activation
                    outlier_count = outlier_count + 1;
                end else begin  // Handle overflow: Set to INT_MAX/INT_MIN
                    if (quantized_activations[i] > 0) begin
                        result = result + ((2**31 - 1) * weights[i]);  // Use INT_MAX with correct parentheses
                    end else begin
                        result = result + ((-2**31) * weights[i]);  // Use INT_MIN with correct parentheses
                    end
                end
            end
        end
    endtask

    // Main convolution computation
    always_ff @(posedge clk or posedge reset) begin
        if (reset) begin
            // Reset the output
            for (int i = 0; i < Hout; i++) begin
                for (int j = 0; j < Wout; j++) begin
                    for (int k = 0; k < Cout; k++) begin
                        conv_output[i][j][k] = 0;
                    end
                end
            end
        end else begin
            // Loop over all output locations
            for (int batch_idx = 0; batch_idx < N; batch_idx++) begin
                for (int out_h = 0; out_h < Hout; out_h++) begin
                    for (int out_w = 0; out_w < Wout; out_w++) begin
                        // Step 1: Extract input tile (2D region of activations)
                        logic [31:0] input_tile [0:Kh-1][0:Kw-1][0:Cin-1];
                        for (int kh = 0; kh < Kh; kh++) begin
                            for (int kw = 0; kw < Kw; kw++) begin
                                for (int cin = 0; cin < Cin; cin++) begin
                                    input_tile[kh][kw][cin] = input_activations[batch_idx][out_h+kh][out_w+kw][cin];
                                end
                            end
                        end

                        // Step 2: Compute for each output channel
                        for (int d2 = 0; d2 < Cout; d2++) begin
                            // Step 3: Quantize activations
                            logic [31:0] flattened_input [0:Kh*Kw*Cin-1];
                            logic [31:0] quantized_input [0:Kh*Kw*Cin-1];
                            logic overflow_flags [0:Kh*Kw*Cin-1];
                            for (int idx = 0; idx < Kh*Kw*Cin; idx++) begin
                                flattened_input[idx] = input_tile[idx / (Kw * Cin)][(idx / Cin) % Kw][idx % Cin];
                            end
                            quantize_activations(flattened_input, quantized_input, overflow_flags);

                            // Step 4: Flatten the weights array for the current output channel (d2)
                            
                            for (int i = 0; i < Kh * Kw * Cin; i++) begin
                                flattened_weights[i] = weights[i / (Kw * Cin)][(i / Cin) % Kw][i % Cin][d2];
                            end

                            // Initialize result
                            result = 0;
                            // Perform the multiplier group computation multiple times
                            for (int iter = 0; iter < 2; iter++) begin  // 2 iterations per tile
                                multiplier_group(quantized_input, flattened_weights, overflow_flags, m, result);
                            end

                            // Step 5: Store the result
                            conv_output[out_h][out_w][d2] = result;
                        end
                    end
                end
            end
        end
    end

endmodule
