from django.conf import settings


def get_all_context(request):
    data = {}
    for key in request.GET.keys():
        data[key] = request.GET.get(key, '')
    return data
