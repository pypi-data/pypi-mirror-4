
from models import LastUsed, ContentType


LIMIT = 10


def use(object, user, key=None, when=None):
    args = {
       'user': user,
       'content_object': object
    }

    if when:
        args['last_used'] = when

    if key:
        args['key'] = key

    obj = LastUsed.objects.create(**args)

    filters = args.copy()

    del filters['content_object']
    filters['content_type'] = obj.content_type

    for lu in LastUsed.objects.filter(**filters)[LIMIT:]:
        lu.delete()

    return obj


def get(model=None, user=None, key=None, limit=0):

    filters = {}
    if model:
        filters['content_type'] = ContentType.objects.get_for_model(model)

    if user:
        filters['user'] = user

    if key:
        filters['key'] = key

    objects = LastUsed.objects.filter(**filters)

    if limit:
        objects = objects[:limit]

    return objects
