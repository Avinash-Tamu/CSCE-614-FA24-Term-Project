module tb_conv2d_pe;

    // Parameters
    parameter int N = 1;            // Batch size
    parameter int Hout = 5;         // Output height (5x5)
    parameter int Wout = 5;         // Output width (5x5)
    parameter int Cin = 1;          // Input channels (grayscale image)
    parameter int Cout = 2;         // Output channels (feature map depth)
    parameter int Kh = 3;           // Kernel height
    parameter int Kw = 3;           // Kernel width
    parameter int m = 2;            // Threshold for handling overflow
    parameter int quantization_threshold = 32'h80000000; // Example threshold for quantization

    // Testbench signals
    logic clk;
    logic reset;
    logic [31:0] input_activations [0:N-1][0:Hout-1][0:Wout-1][0:Cin-1];  // Input activations (4D array)
    logic [31:0] weights [0:Kh-1][0:Kw-1][0:Cin-1][0:Cout-1];              // Weights (4D array)
    logic [31:0] conv_output [0:Hout-1][0:Wout-1][0:Cout-1];                // Output (3D array)

    // Instantiate the conv2d_pe module
    conv2d_pe #(
        .N(N), .Hout(Hout), .Wout(Wout), .Cin(Cin), .Cout(Cout),
        .Kh(Kh), .Kw(Kw)
    ) conv2d_inst (
        .clk(clk),
        .reset(reset),
        .input_activations(input_activations),
        .weights(weights),
        .quantization_threshold(quantization_threshold),
        .m(m),
        .conv_output(conv_output)
    );

    // Clock generation: Toggle every 5 time units
    always #5 clk = ~clk;

    // Test stimulus generation
    initial begin
        // Initialize signals
        clk = 0;
        reset = 1;
        #10 reset = 0;  // Deassert reset after some time

        for (int i = 0; i < N; i = i + 1) begin
            for (int j = 0; j < Hout; j = j + 1) begin
                for (int k = 0; k < Wout; k = k + 1) begin
                    input_activations[i][j][k][0] = 32'h1 + (j * Wout + k); // Fill with incremental values (just an example)
                end
            end
        end

        // Initialize weights (3x3 kernel, 1 input channel, 2 output channels)
        for (int i = 0; i < Kh; i = i + 1) begin
            for (int j = 0; j < Kw; j = j + 1) begin
                for (int k = 0; k < Cin; k = k + 1) begin
                    for (int l = 0; l < Cout; l = l + 1) begin
                        if (l == 0) begin
                            weights[i][j][k][l] = 32'h1;  // Initialize first output channel with all ones
                        end else begin
                            weights[i][j][k][l] = 32'h0;  // Initialize second output channel with all zeros
                        end
                    end
                end
            end
        end

        // Apply reset and then stimulus
        #10 reset = 0;  // Deassert reset

        // Wait for the simulation to run
        #200;


        for (int i = 0; i < Hout; i = i + 1) begin
            for (int j = 0; j < Wout; j = j + 1) begin
                for (int k = 0; k < Cout; k = k + 1) begin
                    $display("Conv Output at (%0d,%0d,%0d): %h", i, j, k, conv_output[i][j][k]);
                end
            end
        end

        // End simulation
        $finish;
    end

endmodule
