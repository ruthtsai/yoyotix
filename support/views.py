# support/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import MessageForm
from .models import Message

@login_required(login_url='login')
def contact_form(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            if request.user.is_authenticated:
                message.user = request.user
            message.save()
            return redirect('message_list')  # 成功後導向留言列表頁
    else:
        form = MessageForm()
    return render(request, 'support/contact_form.html', {'form': form})

def message_list(request):
    messages = Message.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'support/message_list.html', {'messages': messages})
