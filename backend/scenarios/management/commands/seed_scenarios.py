from django.core.management.base import BaseCommand

from scenarios.models import DefenseProfile, Scenario, ScenarioDocument
from scenarios.seed_data import DOCUMENTS, SCENARIOS


class Command(BaseCommand):
    help = "Seed educational LLM security scenarios and fake documents"

    def handle(self, *args, **options):
        for item in SCENARIOS:
            scenario, _ = Scenario.objects.update_or_create(id=item["id"], defaults=item)
            DefenseProfile.objects.update_or_create(scenario=scenario, defaults={})

        for raw in DOCUMENTS:
            item = raw.copy()
            scenario = Scenario.objects.get(id=item.pop("scenario_id"))
            ScenarioDocument.objects.update_or_create(scenario=scenario, title=item["title"], defaults=item)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(SCENARIOS)} scenarios and {len(DOCUMENTS)} documents."))
