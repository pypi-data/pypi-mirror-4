
# I need to access the request globally so that the model access
# can use the session. This logic saves a threadlocal before the
# application logic is invoked.

# http://nedbatchelder.com/blog/201008/global_django_requests.html


from threading import currentThread
_requests = {}

def get_request():
    return _requests[currentThread()]

class GlobalRequestMiddleware(object):
    def process_request(self, request):
        _requests[currentThread()] = request
        return None
    def process_response(self, request, response):
        if currentThread() in _requests:
            del _requests[currentThread()]
        return response
