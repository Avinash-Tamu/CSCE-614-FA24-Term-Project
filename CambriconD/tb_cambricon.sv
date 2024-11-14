`timescale 1ns/1ps;
module tb_PE_array_simulator;

  // Parameters
  parameter PE_ARRAY_SIZE_X = 128;
  parameter PE_ARRAY_SIZE_Y = 128;
  parameter INT_MAX = 2147483647;
  parameter INT_MIN = -2147483648;
  parameter INPUT_SIZE = 128;
  parameter THRESHOLD = 100.0;
  parameter N = 60;
  parameter M = 4;

  // Testbench Signals
  real A [INPUT_SIZE-1:0];
  real W [INPUT_SIZE-1:0];
  integer int_dot_product;
  integer quantized_inliers [0:INPUT_SIZE-1];
  logic overflow_flags [0:INPUT_SIZE-1];
  real fp_dot_product;
  
  // Instantiate the PE_array_simulator module
  PE_array_simulator #(PE_ARRAY_SIZE_X, PE_ARRAY_SIZE_Y, INT_MAX, INT_MIN, INPUT_SIZE, THRESHOLD, N, M)
    uut (
      .A(A),
      .W(W),
      .int_dot_product(int_dot_product),
      .quantized_inliers(quantized_inliers),
      .overflow_flags(overflow_flags),
      .fp_dot_product(fp_dot_product)
    );

  // Testbench initialization and stimulus
  initial begin
    // Initialize the input arrays A and W with random values
    integer i;
    for (i = 0; i < INPUT_SIZE; i = i + 1) begin
      A[i] = $random;
      W[i] = $random;
    end

    // Display the initial values of A and W for debugging
    $display("Initial A values:");
    for (i = 0; i < INPUT_SIZE; i = i + 1) begin
      $display("A[%d] = %f", i, A[i]);
    end
    $display("Initial W values:");
    for (i = 0; i < INPUT_SIZE; i = i + 1) begin
      $display("W[%d] = %f", i, W[i]);
    end
    
    // Wait for a few time units to simulate the PE array
    #10;
    
    // Display the results
    $display("\nSimulation Results:");
    $display("Integer Dot Product: %d", int_dot_product);
    $display("Floating Point Dot Product: %f", fp_dot_product);
    $display("Quantized Inliers:");
    for (i = 0; i < INPUT_SIZE; i = i + 1) begin
      $display("quantized_inliers[%d] = %d", i, quantized_inliers[i]);
    end
    $display("Overflow Flags:");
    for (i = 0; i < INPUT_SIZE; i = i + 1) begin
      $display("overflow_flags[%d] = %b", i, overflow_flags[i]);
    end

    // End the simulation
    $finish;
  end

endmodule
