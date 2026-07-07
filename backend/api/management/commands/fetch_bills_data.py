import os
import requests
from django.core.management.base import BaseCommand
from api.models import Bill


class Command(BaseCommand):
    help = "Fetches bill data (119th Congress) from Congress.gov and upserts into the database"

    def handle(self, *args, **kwargs):
        api_key = os.getenv("CONGRESS_API_KEY")
        url = f"https://api.congress.gov/v3/bill/119?api_key={api_key}&limit=250&format=json"

        total_ingested = 0

        while url:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            bills_batch = []

            for bill_data in data["bills"]:
                bill_id = f"{bill_data['type'].lower()}{bill_data['number']}-{bill_data['congress']}"
                latest_action = bill_data.get("latestAction")
                status_text = latest_action.get(
                    "text", "") if latest_action else ""

                bills_batch.append(Bill(
                    bill_id=bill_id,
                    bill_title=bill_data["title"],
                    status=status_text[:50] if status_text else None,
                ))

            Bill.objects.bulk_create(
                bills_batch,
                update_conflicts=True,
                update_fields=["bill_title", "status"],
                unique_fields=["bill_id"],
            )

            total_ingested += len(bills_batch)

            next_url = data.get("pagination", {}).get("next")
            url = f"{next_url}&api_key={api_key}" if next_url else None

            self.stdout.write(
                f"Processed page, total so far: {total_ingested}")

        self.stdout.write(self.style.SUCCESS(
            f"Finished. Total bills ingested: {total_ingested}"))
