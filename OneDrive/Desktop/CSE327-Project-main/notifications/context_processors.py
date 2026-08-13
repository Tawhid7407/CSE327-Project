def unread_notifications(request):
    """Adds unread_count and recent notifications to context globally."""
    if request.user.is_authenticated:
        qs = request.user.notifications.filter(is_read=False)
        return {
            'unread_notifications_count': qs.count(),
            'recent_notifications': request.user.notifications.all()[:5],
        }
    return {'unread_notifications_count': 0, 'recent_notifications': []}
