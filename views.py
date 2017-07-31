# Create your views here.
from django.http.response import HttpResponse

from apps.djangoperm.utils import view_perm_required


@view_perm_required
def test_view(request):
    return HttpResponse(request,'good')