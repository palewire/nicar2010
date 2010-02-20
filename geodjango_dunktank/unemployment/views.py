from django.http import Http404
from mapping.counties.models import County
from unemployment.models import CountyByMonth
from django.views.generic.simple import direct_to_template


def index(request):
    """
    The homepage.
    """
    context = {}
    
    # Query the latest months' data
    try:
        object_list = CountyByMonth.unadjusted.latest()
    except CountyByMonth.DoesNotExist:
        raise Http404
    
    # Add it to the context we'll pass out to the template
    context['object_list'] = object_list
    
    # Grab the latest month as a datetime object
    context['month'] = object_list[0].get_month_obj()
    
    return direct_to_template(request, 'unemployment/index.html', context)
