from models import Change


def add_change(obj, **kw):
    """
    Alias to Change.objects.add_change_for_object
    """
    return Change.objects.add_change_for_object(obj, **kw)


def get_changes_for(obj, **kw):
    """
    Alias to Change.objects.get_changes_for_object
    """
    return Change.objects.get_changes_for_object(obj, **kw)


def get_anonymous_changes_for(obj, **kw):
    """
    Alias to Change.objects.get_anonymous_changes
    """
    return Change.objects.get_changes_for_object(obj, **kw).anonymous()


def get_changes_by(who, **kw):
    """
    Alias to Change.objects.get_changes_by_user
    """
    return Change.objects.get_changes_by_user(who, **kw)
