module cambricon_d #(
    parameter INPUT_SIZE = 128*128,
    parameter WEIGHT_SIZE = 3*3*64,
    parameter OUTPUT_SIZE = 128*128,
    parameter GROUP_SIZE = 32,
    parameter MAX_OUTLIERS_PER_GROUP = 2,
    parameter DELTA_WIDTH = 3,
    parameter WEIGHT_WIDTH = 16,
    parameter FULL_WIDTH = 16
)(
    input logic clk,
    input logic rst_n,
    input logic signed [DELTA_WIDTH-1:0] delta_in [INPUT_SIZE-1:0],
    input logic signed [WEIGHT_WIDTH-1:0] weights [WEIGHT_SIZE-1:0],
    input logic sign_bits_in [INPUT_SIZE-1:0],
    output logic signed [DELTA_WIDTH-1:0] delta_out [OUTPUT_SIZE-1:0],
    output logic sign_bits_out [OUTPUT_SIZE-1:0]
);

    // Internal registers
    logic signed [FULL_WIDTH-1:0] conv_result [OUTPUT_SIZE-1:0];
    logic signed [FULL_WIDTH-1:0] outlier_result [OUTPUT_SIZE-1:0];
    logic is_outlier [INPUT_SIZE-1:0];
    logic signed [FULL_WIDTH-1:0] total_result [OUTPUT_SIZE-1:0];

    // Outlier detection
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < INPUT_SIZE; i++) begin
                is_outlier[i] <= 1'b0;
            end
        end else begin
            for (int i = 0; i < INPUT_SIZE; i++) begin
                is_outlier[i] <= (delta_in[i] == {DELTA_WIDTH{1'b1}}) || (delta_in[i] == {DELTA_WIDTH{1'b0}});
            end
        end
    end

    // Convolution operation
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < OUTPUT_SIZE; i++) begin
                conv_result[i] <= '0;
            end
        end else begin
            for (int i = 0; i < OUTPUT_SIZE; i++) begin
                conv_result[i] <= '0;
                for (int j = 0; j < WEIGHT_SIZE; j++) begin
                    if (i+j < INPUT_SIZE) begin
                        conv_result[i] <= conv_result[i] + $signed({{(FULL_WIDTH-DELTA_WIDTH){delta_in[i+j][DELTA_WIDTH-1]}}, delta_in[i+j]}) * $signed(weights[j]);
                    end
                end
            end
        end
    end

    // Outlier-aware PE array
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < OUTPUT_SIZE; i++) begin
                outlier_result[i] <= '0;
            end
        end else begin
            for (int i = 0; i < OUTPUT_SIZE; i++) begin
                outlier_result[i] <= '0;
                int outlier_count = 0;
                for (int j = 0; j < GROUP_SIZE; j++) begin
                    if ((i*GROUP_SIZE + j) < INPUT_SIZE && is_outlier[i*GROUP_SIZE + j] && outlier_count < MAX_OUTLIERS_PER_GROUP) begin
                        outlier_result[i] <= outlier_result[i] + $signed({{(FULL_WIDTH-DELTA_WIDTH){delta_in[i*GROUP_SIZE + j][DELTA_WIDTH-1]}}, delta_in[i*GROUP_SIZE + j]}) * $signed(weights[j]);
                        outlier_count++;
                    end
                end
            end
        end
    end

    // Combine regular and outlier results
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < OUTPUT_SIZE; i++) begin
                total_result[i] <= '0;
            end
        end else begin
            for (int i = 0; i < OUTPUT_SIZE; i++) begin
                total_result[i] <= conv_result[i] + outlier_result[i];
            end
        end
    end

    // ReLU activation using sign-bit mask
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < OUTPUT_SIZE; i++) begin
                delta_out[i] <= '0;
                sign_bits_out[i] <= 1'b0;
            end
        end else begin
            for (int i = 0; i < OUTPUT_SIZE; i++) begin
                delta_out[i] <= sign_bits_in[i] ? total_result[i][DELTA_WIDTH-1:0] : {DELTA_WIDTH{1'b0}};
                sign_bits_out[i] <= total_result[i][FULL_WIDTH-1];
            end
        end
    end

endmodule
