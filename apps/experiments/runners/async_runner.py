import asyncio


async def _run_async(workload_func, workers: int, workload_kwargs: dict, workload_type: str) -> list[dict]:
    if workload_type == "io":
        tasks = [workload_func(**workload_kwargs) for _ in range(workers)]
    else:
        tasks = [asyncio.to_thread(workload_func, **workload_kwargs) for _ in range(workers)]

    return await asyncio.gather(*tasks)


def run_with_asyncio(workload_func, workers: int, workload_kwargs: dict, workload_type: str) -> list[dict]:
    """
    Executes the workload using asyncio tasks.
    IO workloads run natively with coroutines; CPU workloads are offloaded to threads.
    """
    return asyncio.run(
        _run_async(
            workload_func=workload_func,
            workers=workers,
            workload_kwargs=workload_kwargs,
            workload_type=workload_type,
        )
    )
