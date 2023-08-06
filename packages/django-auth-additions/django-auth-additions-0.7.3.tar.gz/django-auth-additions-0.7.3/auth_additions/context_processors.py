
def auth_backend(request):
    return {'auth_backend': request.session['_auth_user_backend']}