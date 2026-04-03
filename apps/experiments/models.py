from django.db import models


# Create your models here.
class ExperimentRun(models.Model):
    CONCURRENCY_MODELS = [
        ("thread", "Thread"),
        ("process", "Process"),
        ("async", "Async"),
    ]
    WORKLOAD_TYPES = [("cpu", "CPU BOUND"), ("io", "IO BOUND")]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    name = models.CharField(max_length=255, blank=True, null=True)
    concurrency_model = models.CharField(
        max_length=20,
        choices=CONCURRENCY_MODELS,
    )
    workload_types = models.CharField(max_length=20, choices=WORKLOAD_TYPES)
    workers = models.PositiveIntegerField(default=1)
    iterations = models.PositiveIntegerField(default=1000000)
    io_sleep_ms = models.PositiveIntegerField(default=100)
    io_operations = models.PositiveIntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_duration_ms = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    summary = models.JSONField(default=dict,  blank=True)
    error_message = models.TextField( blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        label = self.name or f"run-{self.pk or 'new'}"
        return f"{label}-{self.concurrency_model}-{self.workload_types}"

class WorkerResult(models.Model):
    experiment_run = models.ForeignKey(ExperimentRun, on_delete=models.CASCADE, related_name='worker_results')
    worker_index = models.PositiveIntegerField()
    duration_ms = models.FloatField()
    output = models.JSONField(default=dict, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    thread_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.experiment_run}-{self.worker_index}"
