from apps.features.lostfound.found_items.models import FoundItem

def get_filtered_found_items(request):
    queryset = FoundItem.objects.all().order_by('-id')
    category = request.query_params.get('category')
    found_location = request.query_params.get('found_location')

    if category:
        queryset = queryset.filter(category__label=category)
    if found_location:
        queryset = queryset.filter(found_location=found_location)
    queryset = queryset.filter(status='available')

    try:
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
    except ValueError:
        page, limit = 1, 10

    total = queryset.count()
    start = (page - 1) * limit
    end = start + limit
    items = queryset[start:end]

    return items, total, page, limit
