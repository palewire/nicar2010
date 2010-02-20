"""
Utilities for loading boundaries into our Geodjango database.
"""
import os
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping

# The location of this directory
this_dir = os.path.dirname(__file__)
# The location of our source shapefile.
shp_file = os.path.join(this_dir, 'data/co06_d00.shp')


def specs():
    """
    Examine our source shapefile and print out some basic data about it.
    
    We can use this to draft the model where we store it in our system.
    
    Done according to documentation here: http://geodjango.org/docs/layermapping.html
    
    Example usage:
    
        >> from mapping.counties import load; load.specs();
    
    """
    # Crack open the shapefile
    ds = DataSource(shp_file)
    # Access the data layer
    layer = ds[0]
    # Print out all kinds of goodies
    print "Fields: %s" % layer.fields
    print "Number of features: %s" % len(layer)
    print "Geometry Type: %s" % layer.geom_type
    print "SRS: %s" % layer.srs


def shp():
    """
    Load the ESRI shapefile from the Census in the County model.
    
    Example usage:
    
        >> from mapping.counties import load; load.shp();
    
    """
    # Import the database model where we want to store the data
    from mapping.counties.models import County
    
    # A crosswalk between the fields in our database and the fields in our
    # source shapefile
    shp2db = {
        'polygon_4269': 'Polygon',
        'state_fips_code': 'STATE',
        'county_fips_code': 'COUNTY',
        'name': 'NAME',
    }
    # Load our model, shape, and the map between them into GeoDjango's magic
    # shape loading function (I also slipped the source coordinate system in
    # there. The Census says they put everything in NAD 83, which translates
    # to 4269 in the SRID id system.)
    lm = LayerMapping(County, shp_file, shp2db, source_srs=4269)
    # Fire away!
    lm.save(verbose=True)


def fix_dupes():
    """
    The Census breaks some counties into more than one shape. It happens when
    a county contains disconnected areas, like islands.
    
    This is a pain in the butt.
    
    To fix it, this function will consolidate duplicates into a single
    "multipolygon."
    
    Example usage: 
    
        >> from mapping.counties import load; load.fix_dupes();

    """
    from django.db.models import Count
    from mapping.counties.models import County
    
    # Group and count the county names that appear more than once
    dupe_list = County.objects.values('name').annotate(
        count=Count('name')).filter(count__gt=1)

    # Loop through each of the dupes
    for dupe in dupe_list:
        # Select all the records with that name
        this_list = County.objects.filter(name=dupe['name'])
        # Print out what you're up to
        print "Consolidating %s shapes for %s county" % (
            this_list.count(),
            dupe['name'],
            )
        # Use GeoDjango magic to consolidate all of their shapes into
        # one big multipolygon
        this_multipolygon = this_list.unionagg()
        # Create a new County record with the unified shape and the rest of
        # the data found in each of the dupes.
        this_obj = County.objects.create(
            name = this_list[0].name,
            state_fips_code = this_list[0].state_fips_code,
            county_fips_code = this_list[0].county_fips_code,
            polygon_4269 = this_multipolygon,
        )
        # Delete all of the duplicates
        [i.delete() for i in 
            County.objects.filter(name=dupe['name']).exclude(id=this_obj.id)]


def extras():
    """
    Load some of the extra data we want for our model that's not included
    in the source shapefile. 
        
        * The combined FIPS
        * The slug field
        * The ForeignKey connection to a State model.
        * The same polygon stored in an OpenLayers friendly SRID (900913)
        * Simplified versions of our polygons that contain few points
        
    Example usage:
    
        >> from mapping.counties import load; load.extras();
        
    """
    from django.template.defaultfilters import slugify
    from mapping.counties.models import County, State
    
    calif, c = State.objects.get_or_create(
        name='California', 
        slug='california'
        )
    
    for obj in County.objects.all():
        print "Filling in extra data for %s" % obj.name
        obj.fips_code = "".join([obj.state_fips_code, obj.county_fips_code])
        obj.slug = slugify(obj.name)
        obj.state = calif
        obj.polygon_900913 = obj.polygon_4269
        obj.set_simple_polygons()

def all():
    """
    Wrap it all together and load everything
    
    Example usage:
        
        >> from mapping.counties import load; load.all()

    """
    shp()
    fix_dupes()
    extras()




