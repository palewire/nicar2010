from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from mapping.counties.models import County, State


class CountyAdmin(OSMGeoAdmin):
    fieldsets = (
        (('Metadata'),
           {'fields': (
                'name', 'slug', 'state', 'state_fips_code',
                'county_fips_code', 'fips_code',
           )}
        ),
        (('Boundaries'),
            {'fields': (
                'polygon_4269', 'simple_polygon_4269',
                'polygon_900913', 'simple_polygon_900913',
            )}
        ),
     )
    list_display = ('name', 'state')
    search_fields = ['name',]
    list_filter = ('state',)
    # Admin map settings
    layerswitcher = False
    scrollable = False
    map_width = 700
    map_height = 600
    openlayers_url = 'http://openlayers.org/api/2.8/OpenLayers.js' 
    
admin.site.register(County, CountyAdmin)


class StateAdmin(OSMGeoAdmin):
    pass

admin.site.register(State, StateAdmin)

