import os
import time
import requests
from django.core.management.base import BaseCommand
from api.models import Member, Donor


def get_with_retry(url, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 429:
            wait = 2 ** attempt  # exponential backoff: 1, 2, 4, 8, 16 seconds
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response
    raise Exception(f"Max retries exceeded for {url}")


class Command(BaseCommand):
    help = "Fetches FEC incumbent candidates and their total receipts, matched to existing Members"

    def handle(self, *args, **kwargs):
        api_key = os.getenv("FEC_API_KEY")
        matched = 0
        unmatched = 0

        for office in ["H", "S"]:
            url = f"https://api.open.fec.gov/v1/candidates/?api_key={api_key}&office={office}&cycle=2026&incumbent_challenge=I&per_page=100"

            while url:
                response = get_with_retry(url)
                data = response.json()

                for candidate in data["results"]:
                    fec_name = candidate["name"]
                    last_name, first_part = [p.strip()
                                             for p in fec_name.split(",", 1)]
                    first_name = first_part.split()[0]
                    state = candidate["state"]

                    member = Member.objects.filter(
                        last_name__iexact=last_name,
                        first_name__istartswith=first_name,
                        state__isnull=False,
                    ).first()

                    if not member:
                        unmatched += 1
                        continue

                    totals_url = f"https://api.open.fec.gov/v1/candidate/{candidate['candidate_id']}/totals/?api_key={api_key}&cycle=2026"
                    totals_response = get_with_retry(totals_url)

                    totals_data = totals_response.json().get("results", [])
                    receipts = totals_data[0]["receipts"] if totals_data else 0

                    Donor.objects.update_or_create(
                        fec_candidate_id=candidate["candidate_id"],
                        defaults={"member": member, "total_receipts": receipts}
                    )
                    matched += 1
                    time.sleep(1)

                next_page = data["pagination"]["page"] + 1
                if next_page <= data["pagination"]["pages"]:
                    url = f"https://api.open.fec.gov/v1/candidates/?api_key={api_key}&office={office}&cycle=2026&incumbent_challenge=I&per_page=100&page={next_page}"
                else:
                    url = None

                self.stdout.write(
                    f"Matched so far: {matched}, unmatched: {unmatched}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. Matched: {matched}, Unmatched: {unmatched}"))
