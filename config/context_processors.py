def user_role(request):
    role = getattr(request, 'role', None)
    if role in {'user', 'partner'} and request.user.is_authenticated:
        return {'user_role': role}
    return {'user_role': 'guest'}