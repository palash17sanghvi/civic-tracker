from django.db import models


class Member(models.Model):
    bioguide_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    party = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    chamber = models.CharField(max_length=20, choices=[
                               ('house', 'House'), ('senate', 'Senate')])

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.state}-{self.party})"


class Bill(models.Model):
    bill_id = models.CharField(max_length=20, unique=True)
    bill_title = models.TextField()
    status = models.CharField(max_length=50, blank=True, null=True)
    committee = models.CharField(max_length=50, blank=True, null=True)
    introduced_date = models.DateField()

    def __str__(self):
        return f"{self.bill_title} ({self.status}-{self.committee})"


class Sponsorship(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    is_primary_sponsor = models.BooleanField(default=False)

    class Meta:
        unique_together = ('member', 'bill')

    def __str__(self):
        return f"{self.member} - {self.bill}"
