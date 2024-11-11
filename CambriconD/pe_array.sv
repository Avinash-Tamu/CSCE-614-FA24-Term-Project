module PE_array_simulator (
    input real A [INPUT_SIZE-1:0],  
    input real W [INPUT_SIZE-1:0],  
    output integer int_dot_product, 
    output integer quantized_inliers [0:INPUT_SIZE-1]; 
    output real fp_dot_product     
);

parameter PE_ARRAY_SIZE_X = 128;
parameter PE_ARRAY_SIZE_Y = 128;
parameter INT_MAX = 2147483647;  // Define INT_MAX 32 bit 
parameter INT_MIN = -2147483648; // Define INT_MIN 32 bit
parameter INPUT_SIZE = 128;
parameter THRESHOLD = 100.0;
parameter N = 60;
parameter M = 4;

integer quantized_A [0:INPUT_SIZE-1];  
logic overflow_flags [0:INPUT_SIZE-1];

function void quantize_activations (
    input real A[], 
    input real W[], 
    output integer quantized_A[], 
    output logic overflow_flags[]
);
    integer outlier_count = 0;
    for (int i = 0; i < INPUT_SIZE; i++) begin
        if (abs(A[i]) > THRESHOLD) begin
            overflow_flags[i] = 1;  
            outlier_count = outlier_count + 1;
        end else begin 
            overflow_flags[i] = 0;  
            quantized_A[i] = $rtoi(A[i]);  
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
    input real A[], 
    input integer quantized_A[], 
    input real W[], 
    input logic overflow_flags[], 
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

task void simulate_PE_array();
    integer int_dot_product, fp_dot_product;
    integer int_multiply, fp_multiply;
    
    quantize_activations (A, W, quantized_A, overflow_flags);
    calculate_dot_product (A, quantized_A, W, overflow_flags, int_dot_product, fp_dot_product, int_multiply, fp_multiply);
endtask

initial begin
    simulate_PE_array();
    assign quantized_inliers = quantized_A;
end

endmodule
