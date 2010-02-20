{% load humanize %}
var map;

function Geometry(symbol, maxSize, maxValue){
    this.symbol = symbol;
    this.maxSize = maxSize;
    this.maxValue = maxValue;
 
    this.getSize = function(value){
        switch(this.symbol) {
            case 'circle': // Returns radius of the circle
            case 'square': // Returns length of a side
                return Math.sqrt(value/this.maxValue)*this.maxSize;
            case 'bar': // Returns height of the bar
                return (value/this.maxValue)*this.maxSize;
            case 'sphere': // Returns radius of the sphere
            case 'cube': // Returns length of a side
                return Math.pow(value/this.maxValue, 1/3)*this.maxSize;
        }
    }
}
 

/* Firing up the map */
function load_map() {

    var max_value = 500000;
    var symbol = new Geometry('circle', 1, max_value);
    var context = {
        getSize: function(feature) {
            return symbol.getSize(feature.data.unemployment) * Math.pow(2,map.getZoom()-1);
        }
    };

    // The boundaries of California
    var max_extent = new OpenLayers.Bounds(-15422000, 4500000, -10942000, 5271000);

    var options = {
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        units: "m",
        numZoomLevels: 18,
        maxResolution: 156543.0339,
        maxExtent: max_extent,
        controls: []
    };

    // Assigning it to an element in the HTML
    map = new OpenLayers.Map('bigmap', options);

    /* Configuration of the map's cosmetic style '*/
    var template = {
        strokeColor : 'rgb(220,0,0)', 
        strokeWidth: 2,
        strokeOpacity: 0.9,
        fillColor : 'rgb(220,0,0)', 
        fillOpacity : 0.5, 
        pointRadius: "${getSize}"
    };
 
    // Assigning the feature style
    var style = new OpenLayers.Style(template, {context: context});
    var styleMap = new OpenLayers.StyleMap({
        'default': style, 
        'select': {
            fillColor: 'red',
            fillOpacity: 0.75
        }
    });

    // create Google Mercator layers
    var gmap = new OpenLayers.Layer.Google(
        "Google Maps",
        {'sphericalMercator': true, type: G_PHYSICAL_MAP}
    );
    map.addLayers([gmap]); 
    
    // Creating a tool to read in WKT formatted geospatial data
    var wkt_f = new OpenLayers.Format.WKT();
    
    // Loop through all the counties and make a vector layer for each
    {% for object in object_list %}
    var point_{{ object.county.id }} = wkt_f.read('{{ object.county.polygon_900913.centroid }}');
    point_{{ object.county.id }}.data = { 
        'unemployment_rate': {{ object.unemployment_rate }},
        'unemployment': {{ object.unemployment }},
        'clean_unemployment': "{{ object.unemployment|intcomma }}",
        'name': "{{ object.county.name }}"
        };
    {% endfor %}
    
    // Create a vector layer that will display all the data
    var county_vector = new OpenLayers.Layer.Vector("Counties");
    county_vector.styleMap = styleMap;
    // Then add all the polygons to the vector layer
    county_vector.addFeatures([{% for object in object_list %}point_{{ object.county.id }}{% if not forloop.last %}, {% endif %}{% endfor %}]);
    
    // Hook some functions to the events that trigger when somebody mouses
    // over the counties on the map
    var selectControl = new OpenLayers.Control.SelectFeature(county_vector, {
        hover: true,
        onSelect: select_feature,
        onUnselect: unselect_feature
    });
                
    // Add the counties to the map
    map.addLayer(county_vector);
    // Turn on the control
    map.addControl(selectControl);
    selectControl.activate();

    // Set the center of the map and zoom there
    var lon = -13302000;
    var lat = 4500000;
    var zoom = 6;
    map.setCenter(new OpenLayers.LonLat(lon, lat), zoom);
    
    function onPopupClose(evt) {
        selectControl.unselect(selectedFeature);
    }
    function select_feature(feature) {
        selectedFeature = feature;
        popup = new OpenLayers.Popup.AnchoredBubble("chicken", 
                                new OpenLayers.LonLat(-12590000, 5150000),
                                new OpenLayers.Size(210,90), // Size of the bubble
                                "<div class='bubblewrap'><p class='county-hed'>" + feature.data.name + "</p><p style='margin-bottom:0px;'>Rate:&nbsp;" + feature.data.unemployment_rate + "%</p><p style='margin:0;'>" + "Total:&nbsp;" + feature.data.clean_unemployment + "</p>" ,
                                null, 
                                false, // closebox?
                                onPopupClose // on close function
                                );
        feature.popup = popup;
        map.addPopup(popup);
    }
    function unselect_feature(feature) {
        map.removePopup(feature.popup);
        feature.popup.destroy();
        feature.popup = null;
    }

    key_popup = new OpenLayers.Popup.AnchoredBubble("chicken", 
                                new OpenLayers.LonLat(-14006000, 3900000),
                                new OpenLayers.Size(200, 80), // Size of the bubble
                                "<div class='bubblewrap'>" + 
                                "<p class='county-hed'>Proporational Map</strong>" +
                                "<p style='margin:0;'><a href='{% url unemployment-month-detail month.year month.month %}'>Switch to thematic map &raquo;</a></p>" +
                                "</div>",
                                null, 
                                false, 
                                onPopupClose
                                );
    map.addPopup(key_popup)


};
