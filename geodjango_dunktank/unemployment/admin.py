from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from unemployment.models import CountyByMonth


class CountyByMonthAdmin(OSMGeoAdmin):
    fieldsets = (
        (('Time and Place'),
           {'fields': (
                'county', 'year', 'month',
                )}
        ),
        (('Unemployment data'),
            {'fields': (
                'labor_force', 'employment',
                'unemployment', 'unemployment_rate',
            )}
        ),
        (('About the data'),
            {'fields': (
                'is_seasonally_adjusted', 'is_preliminary',
                'benchmark',
            )}
        ),
     )
    list_display = (
        'county', 'year', 'month', 'unemployment_rate',
        'is_seasonally_adjusted', 'is_preliminary',
        )
    search_fields = ['county', 'year', 'month']
    list_filter = ('county', 'year', 'is_seasonally_adjusted', 'is_preliminary')
    
admin.site.register(CountyByMonth, CountyByMonthAdmin)
