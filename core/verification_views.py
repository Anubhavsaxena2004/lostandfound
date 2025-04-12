from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Match, FoundItem, LostItem
from .verification_forms import VerificationForm

@login_required
def verify_match(request, match_id):
    match = Match.objects.get(id=match_id)
    
    if request.method == 'POST':
        form = VerificationForm(request.POST, match_id=match_id)
        if form.is_valid():
            form.save_answers()
            messages.success(request, "Verification successful! You can now connect with the finder.")
            return redirect('item-list')
    else:
        form = VerificationForm(match_id=match_id)

    return render(request, 'lostandfound/verify_match.html', {'form': form, 'match': match})
