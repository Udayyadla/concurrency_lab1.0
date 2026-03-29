from rest_framework import viewsets
from .models import ExperimentRun
from .serializers import (
    ExperimentRunSerializer,
    ExperimentRunDetailSerializer

    )

# Create your views here.

class ExperimentRunViewSet(viewsets.ModelViewSet):
    queryset = ExperimentRun.objects.all().order_by('-created_at')
    def get_serializer_class(self):
        if self.action == 'create':
           return ExperimentRunSerializer
        return ExperimentRunDetailSerializer
