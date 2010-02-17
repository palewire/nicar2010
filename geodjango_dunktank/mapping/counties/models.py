from django.contrib.gis.db import models


class County(models.Model):
    """
    An administrative unit created by one of our fine state governments.
    """
    # The name of the county
    name = models.CharField(max_length=300)
    slug = models.SlugField(null=True)
    
    # The state
    state = models.ForeignKey('State', null=True)
    
    # They county's ID codes
    state_fips_code = models.CharField(max_length=2)
    county_fips_code = models.CharField(max_length=3)
    fips_code = models.CharField(max_length=5)
    
    # The boundaries of the county
    polygon_4269 = models.MultiPolygonField(srid=4269)
    # A simplified version of the county boundaries that contains fewer points
    simple_polygon_4269 = models.MultiPolygonField(srid=4269, 
        null=True, blank=True)
    
    # A copy of the boundaries in the coordinate system
    # favored by OpenLayers' implementation of Google Maps
    polygon_900913 = models.MultiPolygonField(srid=900913,
        null=True, blank=True)
    simple_polygon_900913 = models.MultiPolygonField(srid=900913,
        null=True, blank=True)
    
    # Meta
    created = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)
    
    # Managers
    objects = models.GeoManager()
    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Counties'
    
    def __unicode__(self):
        return self.name
        
    def set_simple_polygons(self, tolerance=200):
        """
        Simplifies the source polygons so they don't use so many points.
        
        Provide a tolerance score the indicates how sharply the
        the lines should be redrawn.
        
        Returns True if successful.
        """
        from django.contrib.gis.gdal import OGRGeometry, OGRGeomType
        srid_list = [4269, 900913]
        for srid in srid_list:
            # Fetch the source polygon
            source_field_name = 'polygon_%s' % str(srid)
            source = getattr(self, source_field_name)
            # Fetch the target polygon where the result will be saved
            target_field_name = 'simple_%s' % source_field_name
            target = getattr(self, target_field_name)
            # Transform the source out of lng/lat before the simplification
            copy = source.transform(900913, clone=True)
            # Simplify the source
            simple = copy.simplify(tolerance, True)
            # If it's a polygon, convert it to a MultiPolygon
            if simple.geom_type == 'Polygon':
                mp = OGRGeometry(OGRGeomType('MultiPolygon'))
                simple.transform(srid)
                mp.add(simple.wkt)
                target = mp.wkt
            # Otherwise just save out right away
            else:
                simple.transform(4269)
                target = simple.wkt
            
            # Set the attribute
            setattr(self, target_field_name, target)
        
        # Save out
        self.save()
        return True


class State(models.Model):
    """
    One of these United States.
    
    Mostly just to demostrate how you can link models together. If you were
    doing this for real, you'd probably want to put some polygon fields on
    this guy too.
    """
    name = models.CharField(max_length=150)
    slug = models.SlugField()
    created = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)
    objects = models.GeoManager()
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    

