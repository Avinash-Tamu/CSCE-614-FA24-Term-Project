module cambricon_d_tb;
    parameter INPUT_SIZE = 128*128;
    parameter WEIGHT_SIZE = 3*3*64;
    parameter OUTPUT_SIZE = 128*128;
    parameter DELTA_WIDTH = 3;
    parameter WEIGHT_WIDTH = 16;
    parameter FULL_WIDTH = 16;

    logic clk;
    logic rst_n;
    logic signed [DELTA_WIDTH-1:0] delta_in [INPUT_SIZE-1:0];
    logic signed [WEIGHT_WIDTH-1:0] weights [WEIGHT_SIZE-1:0];
    logic sign_bits_in [INPUT_SIZE-1:0];
    logic signed [DELTA_WIDTH-1:0] delta_out [OUTPUT_SIZE-1:0];
    logic sign_bits_out [OUTPUT_SIZE-1:0];

    // Instantiate the Cambricon-D module
    cambricon_d #(
        .INPUT_SIZE(INPUT_SIZE),
        .WEIGHT_SIZE(WEIGHT_SIZE),
        .OUTPUT_SIZE(OUTPUT_SIZE),
        .DELTA_WIDTH(DELTA_WIDTH),
        .WEIGHT_WIDTH(WEIGHT_WIDTH),
        .FULL_WIDTH(FULL_WIDTH)
    ) dut (.*);

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test stimulus
    initial begin
        // Initialize inputs
        rst_n = 0;
        for (int i = 0; i < INPUT_SIZE; i++) begin
            delta_in[i] = $random;
            sign_bits_in[i] = $random;
        end
        for (int i = 0; i < WEIGHT_SIZE; i++) begin
            weights[i] = $random;
        end

        // Apply reset
        #20 rst_n = 1;

        // Wait for some clock cycles
        repeat(10) @(posedge clk);

        // Apply new inputs
        for (int i = 0; i < INPUT_SIZE; i++) begin
            delta_in[i] = $random;
            sign_bits_in[i] = $random;
        end

        // Wait for processing
        repeat(20) @(posedge clk);

        // Check results
        for (int i = 0; i < OUTPUT_SIZE; i++) begin
            $display("delta_out[%0d] = %0h, sign_bits_out[%0d] = %0b", i, delta_out[i], i, sign_bits_out[i]);
        end

        // Finish simulation
        #100 $finish;
    end

    // Optional: Add assertions here for more thorough verification

endmodule
