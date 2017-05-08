from django.shortcuts import render

# Create your views here.
from django.http.response import HttpResponse
from djangoperm.utils import view_perm_required

@view_perm_required(
            'GET','POST','HEAD','PUT',
            'DELETE','CONNECT','OPTIONS',
            'TRACE','PATCH','MOVE','COPY',
            'LINK','UNLINK','WRAPPED')
def test_view(request):
    return HttpResponse(request,'good')