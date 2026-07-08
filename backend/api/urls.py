from django.urls import path
from . import views

urlpatterns = [
    path('insights/top-fundraisers/', views.top_fundraisers),
    path('insights/party-averages/', views.party_fundraising_averages),
    path('insights/top-sponsors/', views.top_sponsors),
]
