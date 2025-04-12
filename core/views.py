from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import FoundItem, LostItem, VerificationQuestion, Message
from .forms import FoundItemForm, LostItemForm
from .verification_forms import VerificationForm

def status_counts(request):
    counts = {
        'waiting': FoundItem.objects.filter(status='FOUND_WAITING').count(),
        'custody': FoundItem.objects.filter(status='IN_CUSTODY').count(),
        'donated': FoundItem.objects.filter(status='DONATED').count(),
        'claimed': FoundItem.objects.filter(status='CLAIMED').count(),
    }
    return JsonResponse(counts)

def home(request):
    update_item_statuses()
    recent_lost_items = LostItem.objects.filter(status='REPORTED').order_by('-date_submitted')[:3]
    recent_found_items = FoundItem.objects.exclude(status__in=['DONATED', 'CLAIMED']).order_by('-date_submitted')[:3]
    return render(request, 'lostandfound/index.html', {
        'recent_lost_items': recent_lost_items,
        'recent_found_items': recent_found_items
    })


def submit_found_item(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            found_item = form.save(commit=False)
            found_item.status = 'FOUND_WAITING'
            
            if request.user.is_authenticated:
                found_item.submitter = request.user
                # Use authenticated user's info if fields are empty
                if not found_item.submitter_name:
                    found_item.submitter_name = request.user.get_full_name()
                if not found_item.submitter_email:
                    found_item.submitter_email = request.user.email
            
            found_item.save()
            messages.success(request, "Item submitted successfully!")
            return redirect('item_list')
    else:
        form = FoundItemForm()
    return render(request, 'lostandfound/found_item_submission.html', {'form': form})


def submit_lost_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            lost_item = form.save(commit=False)
            lost_item.submitter = request.user
            lost_item.save()
            return redirect('item_list')
    else:
        form = LostItemForm()
    return render(request, 'lostandfound/lost_item_submission.html', {'form': form})

def item_list(request):
    update_item_statuses()
    found_items = FoundItem.objects.exclude(status__in=['DONATED', 'CLAIMED']).order_by('-date_submitted')
    lost_items = LostItem.objects.filter(status='REPORTED').order_by('-date_submitted')
    return render(request, 'lostandfound/item_list.html', {
        'found_items': found_items,
        'lost_items': lost_items
    })

def all_items(request):
    update_item_statuses()
    found_items = FoundItem.objects.all().order_by('-date_submitted')
    lost_items = LostItem.objects.all().order_by('-date_submitted')
    return render(request, 'lostandfound/all_items.html', {
        'found_items': found_items,
        'lost_items': lost_items,
        'show_all': True
    })

@login_required
def verify_claim(request, item_id):
    found_item = get_object_or_404(FoundItem, pk=item_id)
    
    # Get potential matching lost items
    lost_items = LostItem.objects.filter(
        description__icontains=found_item.description,
        brand=found_item.brand,
        color=found_item.color
    ).exclude(user=found_item.submitter)
    
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            # Verify answers against the found item's verification answers
            if all(q.answer == form.cleaned_data[f'question_{q.id}'] 
                  for q in form.questions):
                # Verification successful - allow connection
                found_item.status = 'CLAIMED'
                found_item.claimed_by = request.user
                found_item.save()
                
                # Create verified connection
                Message.objects.create(
                    found_item=found_item,
                    sender=request.user,
                    content="Verification successful - connection established",
                    is_verified=True
                )
                
                messages.success(request, 'Verification successful! Secure connection established.')
                return redirect('view_chat', item_id=item_id)
            else:
                # Verification failed - block connection
                Message.objects.create(
                    found_item=found_item,
                    sender=request.user,
                    content="Failed verification attempt",
                    is_verified=False
                )
                messages.error(request, 'Verification failed. Connection blocked.')
                return redirect('item_list')
    else:
        form = VerificationForm()
        
    return render(request, 'lostandfound/verify_claim.html', {
        'found_item': found_item,
        'lost_items': lost_items,
        'form': form,
        'verification_questions': VerificationQuestion.objects.filter(is_active=True)
    })

def update_item_statuses():
    """Check and update item statuses based on time elapsed"""
    now = timezone.now()
    found_items = FoundItem.objects.filter(status='FOUND_WAITING')
    
    for item in found_items:
        if now - item.date_submitted > timedelta(days=4):
            item.status = 'IN_CUSTODY'
            item.custody_date = now
            item.save()
        
        if item.scheduled_donation_date and now.date() >= item.scheduled_donation_date:
            item.status = 'DONATED'
            item.donation_date = now
            item.save()
