from concurrent.futures import ProcessPoolExecutor,as_completed


def run_with_processes(workload_func, workers: int, workload_kwargs: dict) -> list[dict]:
    """
    Executes the workload using a process pool.
    Returns a list of worker result dictionaries.
    """
    results = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(workload_func, **workload_kwargs) for _ in range(workers)]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    return results
