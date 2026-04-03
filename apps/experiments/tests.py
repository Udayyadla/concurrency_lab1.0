from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ExperimentRun


class ExperimentApiTests(APITestCase):
    def test_create_experiment_defaults_to_pending(self):
        response = self.client.post(
            reverse("experiments-list"),
            {
                "name": "thread cpu test",
                "concurrency_model": "thread",
                "workload_types": "cpu",
                "workers": 2,
                "iterations": 100,
                "io_sleep_ms": 1,
                "io_operations": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")

    def test_run_thread_experiment_creates_worker_results(self):
        experiment = ExperimentRun.objects.create(
            name="thread run",
            concurrency_model="thread",
            workload_types="cpu",
            workers=2,
            iterations=100,
        )

        response = self.client.post(
            reverse("experiments-run", kwargs={"pk": experiment.pk}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        experiment.refresh_from_db()
        self.assertEqual(experiment.status, "completed")
        self.assertEqual(experiment.worker_results.count(), 2)
        self.assertIn("wall_clock_duration_ms", experiment.summary)

    def test_run_async_io_experiment_completes(self):
        experiment = ExperimentRun.objects.create(
            name="async run",
            concurrency_model="async",
            workload_types="io",
            workers=2,
            io_operations=2,
            io_sleep_ms=1,
        )

        response = self.client.post(
            reverse("experiments-run", kwargs={"pk": experiment.pk}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        experiment.refresh_from_db()
        self.assertEqual(experiment.status, "completed")
        self.assertEqual(experiment.worker_results.count(), 2)
