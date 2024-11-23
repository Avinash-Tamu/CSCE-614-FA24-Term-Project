module SFU #(parameter INT_MAX = 2147483647,  // Define INT_MAX 32 bit 
parameter INT_MIN = -2147483648, // Define INT_MIN 32 bit
parameter INPUT_SIZE = 128)(
    input logic  sign_bits [INPUT_SIZE],   //dram out
    input real delta_input [INPUT_SIZE],     // need to check  
    input int quantized_inliers [INPUT_SIZE],   
    input logic  outlier_bitmap [INPUT_SIZE],   // same as pe array "overflow_flags"
    output real updated_values [INPUT_SIZE],    
    output logic overflow_flags [INPUT_SIZE] 
);




real decompressed_inliers [INPUT_SIZE] ;
real decompressed_outliers [INPUT_SIZE] ;
real relu_output [INPUT_SIZE] ;

task int2fp_conversion(input int quantized_in [INPUT_SIZE], output real decompressed_out [INPUT_SIZE]);
    for (int i = 0; i < INPUT_SIZE; i++) begin
        if (quantized_in[i] == INT_MIN) begin
            decompressed_out[i] = 0;  
            overflow_flags[i] = 1;
        end else begin
            decompressed_out[i] = $itor(quantized_in[i]); 
            overflow_flags[i] = 0;
        end
    end
endtask

task decompress_outliers (input logic bitmap [INPUT_SIZE], input real delta_in [INPUT_SIZE], output real outlier_out [INPUT_SIZE]);
    for (int i=0;i<INPUT_SIZE;i++) begin
        if(bitmap[i]) begin
           outlier_out[i] =  delta_in[i];

        end else begin
            outlier_out[i] = 0.0;
        end
    end
endtask

task relu_func(input logic sign_bits [INPUT_SIZE], input real delta_in [INPUT_SIZE], output real relu_out [INPUT_SIZE]);
    for (int i = 0; i < INPUT_SIZE; i++) begin
        if (sign_bits[i]) begin
            relu_out[i] = delta_in[i]; 
        end else begin
            relu_out[i] = 0.0;      
        end
    end
endtask
/*
task read_Add_Write()
    //dont know what to do 
    // low bandwidth and high bandwidth

endtask
*/
initial begin
    int2fp_conversion(quantized_inliers,decompressed_inliers);
    decompress_outliers(outlier_bitmap,delta_input,decompressed_outliers);
    relu_func(sign_bits,delta_input,relu_output);
    //read_Add_Write();
end

endmodule


    

