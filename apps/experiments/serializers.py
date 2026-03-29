from rest_framework import serializers
from .models import ExperimentRun, WorkerResult 

class WokerResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerResult
        fields = [
            "id",
            "worker_index",
            "duration_ms",
            "output",
            "pid",
            "thread_name",
            "created_at",


            ]

class ExperimentRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentRun
        fields = [
            "id",
            "name",
            "concurrency_model",
            "workload_types",
            "workers",
            "iterations",
            "io_sleep_ms",
            "io_operations"
        ]

    def validate_workers(self, value):
        if value < 1:
            raise serializers.ValidationError("Workers must be greater than 0")
        if value > 100:
            raise serializers.ValidationError("Workers must be less than 100")
        return value

    def validate_iterations(self, value):
        if value < 1:
            raise serializers.ValidationError("Iterations must be greater than 0")
        return value

    def validate(self,attrs):
        workload_types = attrs.get("workload_types")
        if workload_types == 'cpu':
            # CPU experiments mainly use iterations
            pass
        if workload_types == 'io':
            if attrs.get('io_operations',0) <= 0:
                raise serializers.ValidationError("IO operations must be greater than 0")
            if attrs.get('io_sleep_ms',0) <= 0:
                raise serializers.ValidationError("IO sleep must be greater than 0")
        return attrs

class ExperimentRunDetailSerializer(serializers.ModelSerializer):
    worker_results = WokerResultSerializer(many=True,read_only=True)
    class Meta:
        model = ExperimentRun
        fields = [
            "id",
            "name",
            "concurrency_model",
            "workload_types",
            "workers",
            "iterations",
            "io_sleep_ms",
            "io_operations",
            "status",
            "total_duration_ms",
            "summary",
            "error_message",
            "started_at",
            "finished_at",
            "created_at",
            "worker_results",
        ]
            