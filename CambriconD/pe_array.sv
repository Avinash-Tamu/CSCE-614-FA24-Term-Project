`timescale 1ns/1ps;
module PE_array_simulator #(parameter PE_ARRAY_SIZE_X = 128,
parameter PE_ARRAY_SIZE_Y = 128,
parameter INT_MAX = 2147483647,  // Define INT_MAX 32 bit 
parameter INT_MIN = -2147483648, // Define INT_MIN 32 bit
parameter INPUT_SIZE = 128,
parameter THRESHOLD = 100.0,
parameter N = 60,
parameter M = 4 
)(
    input real A [0:INPUT_SIZE-1],  
    input real W [0:INPUT_SIZE-1],  
    output integer int_dot_product, 
    output integer quantized_inliers [0:INPUT_SIZE-1],
    output  overflow_flags [0:INPUT_SIZE-1],
    output real fp_dot_product     
);



integer quantized_A [0:INPUT_SIZE-1];  
logic overflow_flags [0:INPUT_SIZE-1];

function void quantize_activations (
    input real A[0:INPUT_SIZE-1], 
    input real W[0:INPUT_SIZE-1], 
    output integer quantized_A[0:INPUT_SIZE-1], 
    output logic overflow_flags[0:INPUT_SIZE-1]
);
    integer outlier_count = 0;
    for (int i = 0; i < INPUT_SIZE; i++) begin
        if (A[i]> THRESHOLD) begin
            overflow_flags[i] = 1;  
            outlier_count = outlier_count + 1;
            $display ("ffffff") ;
        end else begin 
            overflow_flags[i] = 0;  
            quantized_A[i] = $rtoi(A[i]); 
            $display ("kkkkkkkkkkkkkkkkkkkk") ;
        end
    end
    
    if (outlier_count > M) begin
        for (int i = 0; i < INPUT_SIZE; i++) begin
            if (overflow_flags[i] == 1) begin
                if (A[i] > 0) begin
                    quantized_A[i] = INT_MAX;
                end else begin
                    quantized_A[i] = INT_MIN;
                end
            end
        end
    end
endfunction

function void calculate_dot_product (
    input real A[0:INPUT_SIZE-1], 
    input integer quantized_A[0:INPUT_SIZE-1], 
    input real W[0:INPUT_SIZE-1], 
    input logic overflow_flags[0:INPUT_SIZE-1], 
    output integer int_dot_product, 
    output real fp_dot_product, 
    output integer int_multiply, 
    output integer fp_multiply
);
    fp_dot_product = 0;
    fp_multiply = 0;
    int_dot_product = 0;
    int_multiply = 0;
    
    for (int i = 0; i < INPUT_SIZE; i++) begin
        if (overflow_flags[i]) begin
            fp_dot_product = fp_dot_product + A[i] * W[i];
            fp_multiply = fp_multiply + 1;
        end else begin
            int_dot_product = int_dot_product + quantized_A[i] * W[i];
            int_multiply = int_multiply + 1;
        end
    end
endfunction

task  simulate_PE_array();
    integer int_dot_product, fp_dot_product;
    integer int_multiply, fp_multiply;
    
    quantize_activations (A, W, quantized_A, overflow_flags);
    calculate_dot_product (A, quantized_A, W, overflow_flags, int_dot_product, fp_dot_product, int_multiply, fp_multiply);
    quantized_inliers = quantized_A;
endtask

initial begin
    simulate_PE_array();
    
end

endmodule
