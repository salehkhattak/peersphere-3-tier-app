from datetime import datetime


def time_ago(dt):
    """Convert datetime to human-readable 'time ago' string."""
    if not dt:
        return ''
    now = datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f'{mins}m ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours}h ago'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days}d ago'
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f'{weeks}w ago'
    else:
        return dt.strftime('%b %d, %Y')
