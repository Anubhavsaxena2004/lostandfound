from django.urls import path
from . import views
from .messaging_views import initiate_chat, view_chat

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('found/', views.submit_found_item, name='submit_found'),
    path('lost/', views.submit_lost_item, name='submit_lost'),
    path('items/', views.item_list, name='item_list'),
    path('items/all/', views.all_items, name='all_items'),
    path('items/<int:item_id>/chat/', initiate_chat, name='initiate_chat'),
    path('items/<int:item_id>/chat/view/', view_chat, name='view_chat'),
    path('items/<int:item_id>/verify/', views.verify_claim, name='verify_claim'),
    path('api/status_counts/', views.status_counts, name='status_counts'),
]
