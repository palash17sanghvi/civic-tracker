from django.db.models import Count, Avg
from django.db.models.functions import Round
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Member, Donor, Sponsorship


@api_view(['GET'])
def top_fundraisers(request):
    members = (
        Member.objects
        .filter(donor__isnull=False)
        .annotate(bills_sponsored=Count('sponsorship', distinct=True))
        .values('first_name', 'last_name', 'party', 'donor__total_receipts', 'bills_sponsored')
        .order_by('-donor__total_receipts')[:10]
    )
    return Response(list(members))


@api_view(['GET'])
def party_fundraising_averages(request):
    data = (
        Donor.objects
        .values('member__party')
        .annotate(
            num_members=Count('id'),
            avg_receipts=Round(Avg('total_receipts'), 2)
        )
        .order_by('-avg_receipts')
    )
    return Response(list(data))


@api_view(['GET'])
def top_sponsors(request):
    data = (
        Member.objects
        .annotate(bills_sponsored=Count('sponsorship'))
        .filter(bills_sponsored__gt=0)
        .values('first_name', 'last_name', 'party', 'bills_sponsored')
        .order_by('-bills_sponsored')[:10]
    )
    return Response(list(data))
