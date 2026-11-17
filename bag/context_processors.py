def bag_count(request):
    bag = request.session.get('bag', {})
    count = sum(bag.values())

    return {'bag_count': count}