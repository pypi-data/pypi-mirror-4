STATUS = {
    200 : '200 OK',
    404 : '404 NOT FOUND',
    500 : '500 ERROR'
}

class HttpResponse(object):
    def __init__(self, status=200, data=''):
        self.status = STATUS[status]
        self.headers = [('Content-Type', 'text/html')]
        self.data = data