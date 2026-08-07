from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    # Mark all as read
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'includes/notifications.html', {'notifications': notifications})


@login_required
def mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save()
    if n.link:
        return redirect(n.link)
    return redirect('notifications:list')
