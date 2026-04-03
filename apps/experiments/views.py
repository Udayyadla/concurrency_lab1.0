from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ExperimentRun
from .serializers import (
    ExperimentRunSerializer,
    ExperimentRunDetailSerializer,
)
from .services.execution_service import ExperimentExecutionService


class ExperimentRunViewSet(viewsets.ModelViewSet):
    queryset = ExperimentRun.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action in {"retrieve", "run"}:
            return ExperimentRunDetailSerializer
        return ExperimentRunSerializer

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        experiment_run = self.get_object()
        ExperimentExecutionService.run_experiment(experiment_run)
        serializer = ExperimentRunDetailSerializer(experiment_run)
        return Response(serializer.data, status=status.HTTP_200_OK)


