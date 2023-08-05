# Create your views here.
from django.http import HttpResponse
from gametex.models import GTO
from latex import pdflatex

def gametex(request):
    try:
        items = request.GET.get('items')
        gtc = request.GET.get('gtc')
        owner = request.GET.get('owner', None)
        fname = pdflatex(items, gtc, owner=owner)

        if fname:
            data = open(fname, 'r').read()
            response = HttpResponse(data, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="consortium.pdf"'
            return response
    except Exception as e:
        return HttpResponse("Whoops! %s" % e.message)