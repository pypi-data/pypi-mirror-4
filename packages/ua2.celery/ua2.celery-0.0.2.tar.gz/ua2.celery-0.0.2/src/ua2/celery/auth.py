
def auth_decorator(view_func):
    def _wrap(request, *args, **kwargs):
        auth_handler = kwargs.get('auth_decorator')
        if auth_handler:
            del kwargs['auth_decorator']
            return auth_handler(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)

    return _wrap
