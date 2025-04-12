from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FoundItem, Message
from .forms import MessageForm

@login_required
def initiate_chat(request, item_id):
    found_item = get_object_or_404(FoundItem, pk=item_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.found_item = found_item
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('view_chat', item_id=item_id)
    else:
        form = MessageForm()
    
    return render(request, 'lostandfound/initiate_chat.html', {
        'found_item': found_item,
        'form': form
    })

@login_required 
def view_chat(request, item_id):
    found_item = get_object_or_404(FoundItem, pk=item_id)
    chat_messages = Message.objects.filter(found_item=found_item).order_by('timestamp')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.found_item = found_item
            message.save()
            return redirect('view_chat', item_id=item_id)
    else:
        form = MessageForm()
    
    return render(request, 'lostandfound/view_chat.html', {
        'found_item': found_item,
        'messages': chat_messages,
        'form': form
    })
