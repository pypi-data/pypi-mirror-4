from django.shortcuts import render
from models import Testrun, Testresult, Project
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.http import HttpResponse

def testrun_list(request):
    projects = Project.objects.filter(active=True)
    return render(request, 'eukalypse_now/testrun/list.html', {"projects": projects})

def testrun_detail(request, testrun_id):
    testrun = get_object_or_404(Testrun, pk=testrun_id)
    return render(request, 'eukalypse_now/testrun/detail.html', {"testrun": testrun})

def testresult_as_reference(request, testresult_id):
    testresult = get_object_or_404(Testresult, pk=testresult_id)
    testresult.become_reference()
    to_json = {"return": "clear"}
    return HttpResponse(simplejson.dumps(to_json), mimetype="application/json")
    
    

def testresult_acknowledge_error(request, testresult_id):
    testresult = get_object_or_404(Testresult, pk=testresult_id)
    testresult.acknowledge_error()
    to_json = {"return": "clear"}
    return HttpResponse(simplejson.dumps(to_json), mimetype="application/json")
    
    
    
