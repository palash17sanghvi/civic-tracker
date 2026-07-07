import os
import requests
from django.core.management.base import BaseCommand
from api.models import Member


def map_chamber(raw_chamber):
    if "House" in raw_chamber:
        return "house"
    elif "Senate" in raw_chamber:
        return "senate"
    return None


class Command(BaseCommand):
    help = "Fetches member data from Congress.gov API and upserts into the database"

    def handle(self, *args, **kwargs):
        api_key = os.getenv("CONGRESS_API_KEY")
        url = f"https://api.congress.gov/v3/member?api_key={api_key}&limit=250&format=json"

        total_ingested = 0

        while url:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            members_batch = []

            for member_data in data["members"]:
                full_name = member_data["name"]
                last_name, first_name = full_name.split(",", 1)

                terms = member_data.get("terms", {}).get("item", [])
                chamber = map_chamber(terms[0]["chamber"]) if terms else None

                members_batch.append(Member(
                    bioguide_id=member_data["bioguideId"],
                    first_name=first_name.strip(),
                    last_name=last_name.strip(),
                    party=member_data.get("partyName"),
                    state=member_data.get("state"),
                    chamber=chamber,
                ))

            Member.objects.bulk_create(
                members_batch,
                update_conflicts=True,
                update_fields=["first_name", "last_name",
                               "party", "state", "chamber"],
                unique_fields=["bioguide_id"],
            )

            total_ingested += len(members_batch)

            next_url = data.get("pagination", {}).get("next")
            url = f"{next_url}&api_key={api_key}" if next_url else None

            self.stdout.write(
                f"Processed page, total so far: {total_ingested}")

        self.stdout.write(self.style.SUCCESS(
            f"Finished. Total members ingested: {total_ingested}"))
