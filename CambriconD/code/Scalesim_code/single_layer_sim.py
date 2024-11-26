import os
import numpy as np
from scalesim.topology_utils import topologies as topo
from scalesim.compute.operand_matrix import operand_matrix as opmat
from scalesim.memory.double_buffered_scratchpad_mem import double_buffered_scratchpad as mem_dbsp
from scalesim.compute.systolic_compute_os import systolic_compute_os,scale_config  # Make sure to properly import your systolic_compute_os

class single_layer_sim:
    def __init__(self):
        self.layer_id = 0
        self.topo = topo()  # Ensure that 'topo' is correctly defined or imported
        self.config = scale_config()  # Assuming scale_config is a correctly defined or imported configuration class

        self.op_mat_obj = opmat()  # Operand matrix object, ensure it's defined or imported correctly
        self.compute_system = None  # This will be set in set_params based on the dataflow type
        self.memory_system = mem_dbsp()  # Memory system object, ensure it's defined or imported correctly

        self.verbose = True
        self.initialize_report_items()

        self.params_set_flag = False
        self.memory_system_ready_flag = False
        self.runs_ready = False
        self.report_items_ready = False

    def initialize_report_items(self):
        # Initialize or reset report-related items
        self.total_cycles = 0
        self.stall_cycles = 0
        self.num_compute = 0
        self.num_mac_unit = 0
        self.overall_util = 0
        self.mapping_eff = 0
        self.compute_util = 0

        # BW and detailed access reports initialization
        self.avg_ifmap_sram_bw = 0
        self.avg_filter_sram_bw = 0
        self.avg_ofmap_sram_bw = 0
        self.avg_ifmap_dram_bw = 0
        self.avg_filter_dram_bw = 0
        self.avg_ofmap_dram_bw = 0

        self.ifmap_sram_start_cycle = 0
        self.ifmap_sram_stop_cycle = 0
        self.ifmap_sram_reads = 0

        self.filter_sram_start_cycle = 0
        self.filter_sram_stop_cycle = 0
        self.filter_sram_reads = 0

        self.ofmap_sram_start_cycle = 0
        self.ofmap_sram_stop_cycle = 0
        self.ofmap_sram_writes = 0

        self.ifmap_dram_start_cycle = 0
        self.ifmap_dram_stop_cycle = 0
        self.ifmap_dram_reads = 0

        self.filter_dram_start_cycle = 0
        self.filter_dram_stop_cycle = 0
        self.filter_dram_reads = 0

        self.ofmap_dram_start_cycle = 0
        self.ofmap_dram_stop_cycle = 0
        self.ofmap_dram_writes = 0

    def set_params(self, layer_id=0, config_obj=None, topology_obj=None, verbose=True):
        self.layer_id = layer_id
        self.config = config_obj if config_obj else self.config
        self.topo = topology_obj if topology_obj else self.topo

        self.op_mat_obj.set_params(layer_id=self.layer_id, config_obj=self.config, topoutil_obj=self.topo)
        config = scale_config()
        scos = systolic_compute_os(config)
        self.dataflow = self.config.get_dataflow()
        if self.dataflow == 'os':
            self.compute_system = systolic_compute_os(self.config)
        elif self.dataflow == 'ws':
            # self.compute_system = systolic_compute_ws(self.config)
            pass
        elif self.dataflow == 'is':
            # self.compute_system = systolic_compute_is(self.config)
            pass

        self.num_mac_unit = self.config.get_array_dims()[0] * self.config.get_array_dims()[1]
        self.verbose = verbose
        self.params_set_flag = True

    def run(self):
        assert self.params_set_flag, 'Parameters are not set. Run set_params()'
        # Fetch operand matrices
        ifmap_matrix = self.op_mat_obj.get_ifmap_matrix()
        filter_matrix = self.op_mat_obj.get_filter_matrix()
        ofmap_matrix = self.op_mat_obj.get_ofmap_matrix()
        
        # Set compute system parameters with operand matrices
        self.compute_system.set_params(ifmap_op_mat=ifmap_matrix,
                                    filter_op_mat=filter_matrix,
                                    ofmap_op_mat=ofmap_matrix)

        # Generate prefetch and demand matrices
        ifmap_prefetch_mat, filter_prefetch_mat = self.compute_system.get_prefetch_matrices()
        ifmap_demand_mat, filter_demand_mat, ofmap_demand_mat = self.compute_system.get_demand_matrices()

        # Configure memory system if not already configured externally
        if not self.memory_system_ready_flag:
            self.configure_memory_system()

        # Service memory requests
        self.memory_system.service_memory_requests(ifmap_demand_mat, filter_demand_mat, ofmap_demand_mat)

        # Mark simulation run as complete
        self.runs_ready = True


    def save_traces(self, top_path):
        assert self.runs_ready, 'Simulation runs are not complete.'
        # Define directory and file paths
        dir_name = os.path.join(top_path, f'layer_{self.layer_id}')
        os.makedirs(dir_name, exist_ok=True)

        # Save traces from memory system
        self.memory_system.print_ifmap_sram_trace(os.path.join(dir_name, 'IFMAP_SRAM_TRACE.csv'))
        self.memory_system.print_filter_sram_trace(os.path.join(dir_name, 'FILTER_SRAM_TRACE.csv'))
        self.memory_system.print_ofmap_sram_trace(os.path.join(dir_name, 'OFMAP_SRAM_TRACE.csv'))

        # If detailed DRAM traces are required, ensure methods are defined to handle them
        # Example: self.memory_system.print_ifmap_dram_trace(os.path.join(dir_name, 'IFMAP_DRAM_TRACE.csv'))

    def calc_report_data(self):
        assert self.runs_ready, 'Simulation runs are not complete.'

        # Calculate total cycles, stalls, and utilization
        self.total_cycles = self.memory_system.get_total_compute_cycles()
        self.stall_cycles = self.memory_system.get_stall_cycles()
        self.overall_util = (self.num_compute * 100) / (self.total_cycles * self.num_mac_unit)

        # Efficiency metrics
        self.mapping_eff = self.compute_system.get_avg_mapping_efficiency() * 100
        self.compute_util = self.compute_system.get_avg_compute_utilization() * 100

        # Bandwidth usage from memory system
        self.avg_ifmap_sram_bw = self.memory_system.get_avg_ifmap_bw()
        self.avg_filter_sram_bw = self.memory_system.get_avg_filter_bw()
        self.avg_ofmap_sram_bw = self.memory_system.get_avg_ofmap_bw()

        self.report_items_ready = True


    def get_layer_id(self):
        assert self.params_set_flag, 'Parameters are not set yet'
        return self.layer_id

    def get_compute_report_items(self):
        if not self.report_items_ready:
            self.calc_report_data()

        items = [self.total_cycles, self.stall_cycles, self.overall_util, self.mapping_eff, self.compute_util]
        return items

    def get_bandwidth_report_items(self):
        if not self.report_items_ready:
            self.calc_report_data()

        items = [self.avg_ifmap_sram_bw, self.avg_filter_sram_bw, self.avg_ofmap_sram_bw]
        items += [self.avg_ifmap_dram_bw, self.avg_filter_dram_bw, self.avg_ofmap_dram_bw]

        return items

    def get_detail_report_items(self):
        if not self.report_items_ready:
            self.calc_report_data()

        items = [self.ifmap_sram_start_cycle, self.ifmap_sram_stop_cycle, self.ifmap_sram_reads]
        items += [self.filter_sram_start_cycle, self.filter_sram_stop_cycle, self.filter_sram_reads]
        items += [self.ofmap_sram_start_cycle, self.ofmap_sram_stop_cycle, self.ofmap_sram_writes]
        items += [self.ifmap_dram_start_cycle, self.ifmap_dram_stop_cycle, self.ifmap_dram_reads]
        items += [self.filter_dram_start_cycle, self.filter_dram_stop_cycle, self.filter_dram_reads]
        items += [self.ofmap_dram_start_cycle, self.ofmap_dram_stop_cycle, self.ofmap_dram_writes]

        return items
