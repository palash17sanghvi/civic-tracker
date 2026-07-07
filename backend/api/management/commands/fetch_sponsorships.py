import os
import requests
from django.core.management.base import BaseCommand
from api.models import Bill, Member, Sponsorship
from datetime import datetime


class Command(BaseCommand):
    help = "Fetches sponsor info for a subset of bills and creates Sponsorship links"

    def handle(self, *args, **kwargs):
        api_key = os.getenv("CONGRESS_API_KEY")

        # Scope: 300 most recently updated bills
        bills = Bill.objects.order_by('-id')[:300]

        linked = 0
        skipped_no_sponsor = 0
        skipped_no_member = 0

        for bill in bills:
            bill_type, bill_number = bill.bill_id.rsplit('-', 1)[0], None
            # bill_id format: "hr134-119" -> need "hr" and "134" and congress "119"
            congress = bill.bill_id.split('-')[-1]
            type_and_number = bill.bill_id.rsplit('-', 1)[0]
            # separate letters from digits, e.g. "hr134" -> "hr", "134"
            i = 0
            while i < len(type_and_number) and not type_and_number[i].isdigit():
                i += 1
            bill_type = type_and_number[:i]
            bill_number = type_and_number[i:]

            url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}?api_key={api_key}&format=json"
            response = requests.get(url)

            if response.status_code != 200:
                self.stdout.write(
                    f"Skipping {bill.bill_id}: HTTP {response.status_code}")
                continue

            data = response.json().get("bill", {})
            sponsors = data.get("sponsors", [])

            introduced_date = data.get("introducedDate")
            if introduced_date:
                bill.introduced_date = datetime.strptime(
                    introduced_date, "%Y-%m-%d").date()
                bill.save(update_fields=["introduced_date"])

            if not sponsors:
                skipped_no_sponsor += 1
                continue

            sponsor_bioguide_id = sponsors[0]["bioguideId"]

            try:
                member = Member.objects.get(bioguide_id=sponsor_bioguide_id)
            except Member.DoesNotExist:
                skipped_no_member += 1
                continue

            Sponsorship.objects.update_or_create(
                member=member,
                bill=bill,
                defaults={"is_primary_sponsor": True}
            )
            linked += 1

            if linked % 50 == 0:
                self.stdout.write(f"Linked {linked} so far...")

        self.stdout.write(self.style.SUCCESS(
            f"Done. Linked: {linked}, skipped (no sponsor): {skipped_no_sponsor}, skipped (member not found): {skipped_no_member}"
        ))
