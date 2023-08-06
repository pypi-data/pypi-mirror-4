__all__ = ['change_added']


from django.dispatch import Signal


change_added = Signal(providing_args=['change'])
