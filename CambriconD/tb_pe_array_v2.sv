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

        // Initialize the input activations (example 5x5 input, 1 channel)
        input_activations[0][0][0][0] = 32'h1;   // Sample values
        input_activations[0][0][1][0] = 32'h2;
        input_activations[0][0][2][0] = 32'h3;
        input_activations[0][0][3][0] = 32'h4;
        input_activations[0][0][4][0] = 32'h5;
        input_activations[0][1][0][0] = 32'h6;
        input_activations[0][1][1][0] = 32'h7;
        input_activations[0][1][2][0] = 32'h8;
        input_activations[0][1][3][0] = 32'h9;
        input_activations[0][1][4][0] = 32'hA;
        input_activations[0][2][0][0] = 32'hB;
        input_activations[0][2][1][0] = 32'hC;
        input_activations[0][2][2][0] = 32'hD;
        input_activations[0][2][3][0] = 32'hE;
        input_activations[0][2][4][0] = 32'hF;
        input_activations[0][3][0][0] = 32'h10;
        input_activations[0][3][1][0] = 32'h11;
        input_activations[0][3][2][0] = 32'h12;
        input_activations[0][3][3][0] = 32'h13;
        input_activations[0][3][4][0] = 32'h14;
        input_activations[0][4][0][0] = 32'h15;
        input_activations[0][4][1][0] = 32'h16;
        input_activations[0][4][2][0] = 32'h17;
        input_activations[0][4][3][0] = 32'h18;
        input_activations[0][4][4][0] = 32'h19;

        // Initialize the weights (example 3x3 kernel, 1 input channel, 2 output channels)
        weights[0][0][0][0] = 32'h1;
        weights[0][1][0][0] = 32'h1;
        weights[0][2][0][0] = 32'h1;
        weights[1][0][0][0] = 32'h0;
        weights[1][1][0][0] = 32'h0;
        weights[1][2][0][0] = 32'h0;
        weights[2][0][0][0] = 32'h0;
        weights[2][1][0][0] = 32'h0;
        weights[2][2][0][0] = 32'h0;

        // Initialize second output channel weights (for simplicity, keeping the same kernel)
        weights[0][0][0][1] = 32'h1;
        weights[0][1][0][1] = 32'h1;
        weights[0][2][0][1] = 32'h1;
        weights[1][0][0][1] = 32'h0;
        weights[1][1][0][1] = 32'h0;
        weights[1][2][0][1] = 32'h0;
        weights[2][0][0][1] = 32'h0;
        weights[2][1][0][1] = 32'h0;
        weights[2][2][0][1] = 32'h0;

        // Apply reset and then stimulus
        #10 reset = 0;  // Deassert reset

        // Wait for the simulation to run
        #200;

        // Display the results
        $display("Conv Output at (0,0,0): %h", conv_output[0][0][0]);
        $display("Conv Output at (0,1,0): %h", conv_output[0][1][0]);
        $display("Conv Output at (1,1,0): %h", conv_output[1][1][0]);
        $display("Conv Output at (0,0,1): %h", conv_output[0][0][1]);
        $display("Conv Output at (1,1,1): %h", conv_output[1][1][1]);

        // End simulation
        $finish;
    end

endmodule
