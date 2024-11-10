module PE_array_simulator;

parameter PE_ARRAY_SIZE_X = 128;
parameter PE_ARRAY_SIZE_Y = 128;
parameter INT_MAX = ;
parameter INT_MIN = ;
parameter INPUT_SIZE = 128 ;
parameter THRESHOLD = ;         
parameter N = 60;            
parameter M = 4;

real A [INPUT_SIZE-1:0];
real W [INPUT_SIZE-1:0];

function void quantize_activations (input real A[], input real W[], output quantized_A [], output overflow_flags []);
    for (int i=0; i< INPUT_SIZE; i++) begin
        if (abs(A[i]) > THRESHOLD) begin
            overflow_flags[i] = 1;
        end else begin 
            overflow_flags[i] = 0;
            quantized_A[i] = $rtoi(A[i])
        end
    end
endfunction

function void calculate_dot_product (input real A[],input quantized_A[], input real W[], input logic overflow_flags[], output integer int_dot_product, output real fp_dot_product, output integer int_multiply, output integer fp_multiply);
   fp_dot_product = 0;
   fp_multiply = 0;
   int_dot_product =0;
   int_multiply =0;
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


task void simulate_PE_array ();
    integer int_dot_product, fp_dot_product;
    integer int_multiply, fp_multiply;
    integer quantized_A [0:INPUT_SIZE-1];    
    logic overflow_flags [0:INPUT_SIZE-1];   

    quantize_activations (A, W, quantized_A, overflow_flags);
    calculate_dot_product (A, quantized_A, W, overflow_flags, int_dot_product, fp_dot_product, int_multiply, fp_multiply);

endtask

initial begin
    simulate_PE_array();
end

endmodule