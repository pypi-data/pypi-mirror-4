from http import HttpResponse

class Core(object):
    views = []
    def __init__(self):
        pass
    
    def add_route(self, url):
        def wrapper(func):
            self.views.append({
                'url': url,
                'view': func
            })
        return wrapper
    
    def work(self, request):
        for v in self.views:
            if v['url'] == request['PATH_INFO']:
                return v['view'](request)
        return HttpResponse(status=404)