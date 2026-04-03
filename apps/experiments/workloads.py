import math
import os
import threading
import time
import asyncio


def cpu_bound_workload(iterations:int) -> dict :
    """
    Simulates CPU-heavy work by doing repeated math operations.
    """
    start = time.perf_counter()
    total = 0

    for i in range(iterations):
        total += math.sqrt((i%100)+1)

    end = time.perf_counter()
    return {
        "workload_result": total,
        "duration_ms": round((end - start) * 1000, 3), #end - start
        "pid":os.getpid(),
        "thread_name": threading.current_thread().name
    }


def io_bound_workload(io_operations: int, io_sleep_ms: int) -> dict :
    """
    Simulates IO-heavy work by reading from a file.
    """
    start = time.perf_counter()
    total = 0
    sleep_seconds = io_sleep_ms / 1000
   
    for i in range(io_operations):
        time.sleep(sleep_seconds)
        total += i

    end = time.perf_counter()
    return {
        "workload_result": total,
        "duration_ms": round((end - start) * 1000, 3), #end - start
        "pid":os.getpid(),
        "thread_name": threading.current_thread().name
    }


async def async_io_bound_workload(io_operations: int, io_sleep_ms: int) -> dict:
    start = time.perf_counter()
    total = 0
    sleep_seconds = io_sleep_ms / 1000

    for i in range(io_operations):
        await asyncio.sleep(sleep_seconds)
        total += i

    end = time.perf_counter()
    return {
        "workload_result": total,
        "duration_ms": round((end - start) * 1000, 3),
        "pid": os.getpid(),
        "thread_name": threading.current_thread().name,
    }

WORKLOAD_MAP = {
    "cpu": cpu_bound_workload,
    "io": io_bound_workload,
}

ASYNC_WORKLOAD_MAP = {
    "cpu": cpu_bound_workload,
    "io": async_io_bound_workload,
}

def get_workload_function(workload_type: str, *, async_mode: bool = False):
    workload_map = ASYNC_WORKLOAD_MAP if async_mode else WORKLOAD_MAP
    try:
        return workload_map[workload_type]
    except KeyError:
        raise ValueError(f"unsupported workload type: {workload_type}")
