from pyramid.httpexceptions import HTTPBadRequest

def check_csrf_token(request):
    token = request.session.get_csrf_token()
    if token != request.params['csrf_token']:
        raise HTTPBadRequest('CSRF token did not match')