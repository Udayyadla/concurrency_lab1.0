from django.contrib import admin
from .models import ExperimentRun, WorkerResult


# Register your models here.
@admin.register(ExperimentRun)
class ExperimentRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "concurrency_model",
        "workload_types",
        "workers",
        "iterations",
        "status",
        "created_at",
    )
    list_filter = ("concurrency_model", "workload_types", "status")
    search_fields = ("name",)


@admin.register(WorkerResult)
class WorkerResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "experiment_run",
        "worker_index",
        "duration_ms",
        "pid",
        "thread_name",
        "created_at",
    )
    list_filter = (
        "experiment_run",
        "worker_index",
        "duration_ms",
        "pid",
        "thread_name",
    )
