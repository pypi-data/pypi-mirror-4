
def set_auth_backend(request):
    if not hasattr(request.user, 'auth_backend'):
        if request.session.has_key('_auth_user_backend'):
            request.user.auth_backend = request.session['_auth_user_backend']
            
class RequestUserBackendMiddleware(object):
    def process_request(self, request):
        set_auth_backend(request)
    
    def process_response(self, request, response):
        set_auth_backend(request)
        return response
