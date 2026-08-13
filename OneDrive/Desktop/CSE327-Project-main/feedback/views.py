from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.decorators import admin_required
from .models import Feedback
from .forms import FeedbackForm


def contact_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect('feedback:contact')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = FeedbackForm(initial=initial)
    return render(request, 'core/contact.html', {'form': form})


@admin_required
def feedback_list(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'admin_panel/feedback.html', {'feedbacks': feedbacks})
