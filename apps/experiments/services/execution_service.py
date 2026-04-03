import statistics
import time

from django.db import transaction
from django.utils import timezone

from ..models import ExperimentRun, WorkerResult
from ..runners.async_runner import run_with_asyncio
from ..runners.process_runner import run_with_processes
from ..runners.thread_runner import run_with_threads
from ..workloads import get_workload_function


class ExperimentExecutionService:
    @classmethod
    def run_experiment(cls, experiment_run: ExperimentRun) -> ExperimentRun:
        if experiment_run.status in {"running", "completed"}:
            raise ValueError("Experiment is already running or completed.")

        workload_func = get_workload_function(
            experiment_run.workload_types,
            async_mode=experiment_run.concurrency_model == "async",
        )
        workload_kwargs = cls._build_workload_kwargs(experiment_run)
        start = time.perf_counter()

        experiment_run.status = "running"
        experiment_run.started_at = timezone.now()
        experiment_run.finished_at = None
        experiment_run.error_message = ""
        experiment_run.summary = {}
        experiment_run.total_duration_ms = None
        experiment_run.save(
            update_fields=[
                "status",
                "started_at",
                "finished_at",
                "error_message",
                "summary",
                "total_duration_ms",
            ]
        )

        try:
            if experiment_run.concurrency_model == "process":
                worker_outputs = run_with_processes(
                    workload_func=workload_func,
                    workers=experiment_run.workers,
                    workload_kwargs=workload_kwargs,
                )
            elif experiment_run.concurrency_model == "thread":
                worker_outputs = run_with_threads(
                    workload_func=workload_func,
                    workers=experiment_run.workers,
                    workload_kwargs=workload_kwargs,
                )
            elif experiment_run.concurrency_model == "async":
                worker_outputs = run_with_asyncio(
                    workload_func=workload_func,
                    workers=experiment_run.workers,
                    workload_kwargs=workload_kwargs,
                    workload_type=experiment_run.workload_types,
                )
            else:
                raise ValueError(f"Unknown concurrency model: {experiment_run.concurrency_model}")

            worker_results = []
            for worker_index, worker_output in enumerate(worker_outputs, start=1):
                worker_results.append(
                    WorkerResult(
                        experiment_run=experiment_run,
                        worker_index=worker_index,
                        duration_ms=worker_output["duration_ms"],
                        output={"workload_result": worker_output["workload_result"]},
                        pid=worker_output["pid"],
                        thread_name=worker_output["thread_name"],
                    )
                )

            total_duration_ms = round((time.perf_counter() - start) * 1000, 3)
            summary = cls._build_summary(worker_outputs, total_duration_ms)

            with transaction.atomic():
                WorkerResult.objects.filter(experiment_run=experiment_run).delete()
                WorkerResult.objects.bulk_create(worker_results)
                experiment_run.status = "completed"
                experiment_run.finished_at = timezone.now()
                experiment_run.total_duration_ms = total_duration_ms
                experiment_run.summary = summary
                experiment_run.save(
                    update_fields=[
                        "status",
                        "finished_at",
                        "total_duration_ms",
                        "summary",
                    ]
                )

        except Exception as exc:
            experiment_run.status = "failed"
            experiment_run.finished_at = timezone.now()
            experiment_run.error_message = str(exc)
            experiment_run.save(
                update_fields=["status", "finished_at", "error_message"]
            )
            raise

        return experiment_run

    @staticmethod
    def _build_workload_kwargs(experiment_run: ExperimentRun) -> dict:
        if experiment_run.workload_types == "cpu":
            return {"iterations": experiment_run.iterations}

        return {
            "io_operations": experiment_run.io_operations,
            "io_sleep_ms": experiment_run.io_sleep_ms,
        }

    @staticmethod
    def _build_summary(worker_outputs: list[dict], total_duration_ms: float) -> dict:
        durations = [worker_output["duration_ms"] for worker_output in worker_outputs]
        return {
            "workers_completed": len(worker_outputs),
            "wall_clock_duration_ms": total_duration_ms,
            "average_worker_duration_ms": round(statistics.fmean(durations), 3),
            "min_worker_duration_ms": round(min(durations), 3),
            "max_worker_duration_ms": round(max(durations), 3),
        }
