import datetime

def created(sender, instance, **kwargs):
    """When an instance is saved, add the created date"""
    if not instance.created:
        instance.created = datetime.datetime.now()

