# Django imports
from django.contrib.auth.decorators import permission_required
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
# Local imports
from models import Query

@permission_required('flatqueries.can_run_query')
def run(request, id):
    query = Query.objects.get(pk=id)
    if request.method=='POST':
        (headers, rows) = query.run()
    else:
        headers = rows = None
    tv = {
        'query': query,
        'headers': headers,
        'rows': rows,        
    }
    tv.update(csrf(request))
    return render_to_response('flatqueries/run.html', tv)
