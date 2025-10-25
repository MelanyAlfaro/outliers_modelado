from enum import StrEnum


class EventTypes(StrEnum):
    # Simulation
    SIMULATION_START = "simulation_start"
    SIMULATION_END = "simulation_end"

    # Master
    MASTER_RECEIVE_MSG = "master_receive_msg"
    MASTER_START_PROCESSING_MSG = "master_start_processing_msg"
    MASTER_END_PROCESSING_MSG = "master_end_processing_msg"

    # Lazy
    LAZY_RECEIVE_EXT_MSG = "lazy_receive_ext_msg"
    LAZY_RECEIVE_INT_MSG = "lazy_receive_int_msg"
    LAZY_START_PROCESSING_MSG = "lazy_start_processing_msg"
    LAZY_END_PROCESSING_MSG = "lazy_end_processing_msg"

    # Worker
    WORKER_RECEIVE_EXT_MSG = "worker_receive_ext_msg"
    WORKER_RECEIVE_INT_MSG = "worker_receive_int_msg"
    WORKER_START_PROCESSING_MSG = "worker_start_processing_msg"
    WORKER_END_PROCESSING_MSG = "worker_end_processing_msg"
