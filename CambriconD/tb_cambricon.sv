`timescale 1ns/1ps

`include "pe_array.sv"
`include "SFU.sv"
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
  real A [INPUT_SIZE];
  real W [INPUT_SIZE];
  integer int_dot_product;
  integer quantized_inliers [INPUT_SIZE];
  logic overflow_flags [INPUT_SIZE];
  real fp_dot_product;



    logic  sign_bits [INPUT_SIZE];
     real delta_input [INPUT_SIZE];       
     logic  outlier_bitmap [INPUT_SIZE]  ;
     real updated_values [INPUT_SIZE];    
     logic sfu_flags [INPUT_SIZE];
  
  PE_array_simulator #(PE_ARRAY_SIZE_X, PE_ARRAY_SIZE_Y, INT_MAX, INT_MIN, INPUT_SIZE, THRESHOLD, N, M)
    pe_array_inst (
      .A(A),
      .W(W),
      .int_dot_product(int_dot_product),
      .quantized_inliers(quantized_inliers),
      .overflow_flags(overflow_flags),
      .delta_out(delta_input),
      .fp_dot_product(fp_dot_product)
    );

SFU #(INT_MAX, INT_MIN, INPUT_SIZE) 
    sfu_inst (
    .sign_bits(sign_bits),
    .delta_input(delta_input),
    .quantized_inliers(quantized_inliers),
    .outlier_bitmap(overflow_flags),
    .updated_values(updated_values),
    .overflow_flags(sfu_flags)
);

  // Testbench initialization and stimulus
  initial begin
    // Initialize the input arrays A and W with random values
    integer i;
    for (i = 0; i < INPUT_SIZE; i = i + 1) begin
      A[i] = $random;
      W[i] = $random;
    end
    #10;
    // Display the initial values of A and W for debugging
    $display("Initial A values:");
    for (i = 0; i < INPUT_SIZE; i = i + 1) begin
      $display("A[%d] = %f", i, A[i]);
    end
    $display("Initial W values:");
    for (i = 0; i < INPUT_SIZE; i = i + 1) begin
      $display("W[%d] = %f", i, W[i]);
    end
    
    #1000;
    
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

    $finish;
  end

endmodule
