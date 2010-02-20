from django.http import Http404
from mapping.counties.models import County
from unemployment.models import CountyByMonth
from django.views.generic.simple import direct_to_template


def render_map(request, object_list):
    """
    Feeds data out to our map template.
    """
    context = {}

    # Add it to the context we'll pass out to the template
    context['object_list'] = object_list
    
    # Grab the latest month as a datetime object
    context['month'] = object_list[0].get_month_obj()
    
    # If data exists for the next month, pass it along
    next = object_list[0].get_next_month()
    if CountyByMonth.objects.filter(year=next.year, month=next.month):
        context['next_month'] = next

    # Same for the previous month
    prev = object_list[0].get_previous_month()
    if CountyByMonth.objects.filter(year=prev.year, month=prev.month):
        context['previous_month'] = prev
    
    return direct_to_template(request, 'unemployment/map.html', context)


def index(request):
    """
    The homepage.
    
    Reports the latest month's data.
    """    
    # Query the latest months' data
    try:
        object_list = CountyByMonth.unadjusted.latest()
    except CountyByMonth.DoesNotExist:
        raise Http404
    
    return render_map(request, object_list)
    
    
def month_detail(request, year, month):
    """
    Reports the data for a particular month.
    """
    try:
        object_list = CountyByMonth.unadjusted.filter(year=year, month=month)
    except:
        raise Http404
    if not object_list:
        raise Http404
    return render_map(request, object_list)
    
