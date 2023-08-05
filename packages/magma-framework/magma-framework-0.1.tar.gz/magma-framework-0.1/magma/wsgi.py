from wsgiref.simple_server import make_server
from magma.core import Core
from magma.http import HttpResponse

app = Core()
   
@app.add_route('/')
def home(request):
    return HttpResponse(status=200, data=['Welcome'])
    
@app.add_route('/about/')
def about(request):
    return HttpResponse(status=200, data=['Magma v0.1'])

def application(request, response):
    http = app.work(request)
    response(http.status, http.headers)
    return http.data

server = make_server('localhost', 8000, application)
server.serve_forever()