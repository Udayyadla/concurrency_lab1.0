from django.db import transaction
from django.utils import timezone

from experiments.models import ExperimentRun, WorkerResult
from experiments.runners.process_runner import run_with_processes
from experiments.runners.thread_runner import run_with_threads
from experiments.workloads import get_workload_function


class ExperimentExecutionService:
    @classmethod
    def run_experiment(cls, experiment_run: ExperimentRun, workers:int, iterations:int):
        """
        Runs an experiment using the specified concurrency model.

        Args:
            experiment_run: The ExperimentRun instance to run.
            workers: The number of workers to use.
            iterations: The number of iterations to run the workload.

        Returns:
            None

        Raises:
            None
        """
        if experiment_run.status == "running" or experiment_run.status == "completed":
            raise ValueError("Experiment is already running or completed.")
        workload_func = get_workload_function(experiment_run.workload_types)
        experiment_run.status = "running"
        experiment_run.save(update_fields=["status"])
        
        try:
            if experiment_run.concurrency_model == "process":
                worker_outputs = run_with_processes(workload_func=workload_func,
                                                    workers=experiment_run.workers, 
                                                    iterations=experiment_run.iterations)
            elif experiment_run.concurrency_model == "thread":
                worker_outputs = run_with_threads(workload_func=workload_func,
                                                  workers=experiment_run.workers, 
                                                  iterations=experiment_run.iterations)
            else:
                raise ValueError(f"Unknown concurrency model: {experiment_run.concurrency_model}")
            
            worker_results = []
            for worker_index, worker_output in enumerate(worker_outputs,start=1):
                worker_result = WorkerResult(experiment_run=experiment_run,
                                             worker_index=worker_index,
                                             duration_ms=worker_output["duration_ms"],
                                             output=worker_output["output"],
                                             pid=worker_output["pid"],
                                             thread_name=worker_output["thread_name"])
                worker_results.append(worker_result)

            with transaction.atomic():
                WorkerResult.objects.filter(experiment_run=experiment_run).delete()
                worker_result.objects.bulk_create(worker_results)
                experiment_run.status = "completed"
                experiment_run.finished_at = timezone.now() if hasattr(experiment_run, 'completed_at') else None
                experiment_run.total_duration_ms = sum([worker.duration_ms for worker in worker_results])
                experiment_run.save(
                    update_fields=[
                        "status",
                        "finished_at",
                        "total_duration_ms",])

        except Exception as e:
            experiment_run.status = "failed"
            experiment_run.finished_at = timezone.now()
            experiment_run.error_message = str(e)
            experiment_run.save(update_fields=["status", "error_message"])
            raise

        return experiment_run