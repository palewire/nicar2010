{% load humanize %}
var map;

/* 
    Configuration of the thematic map's stratification 
    i.e. Which numbers go with which colors.
*/
var setRGB = function ( green ){
    green = parseInt(green);
    green += ""
    rgb = 'rgb(220,' + green + ',0)'
    return rgb;
}
var context = {
    getColor: function(feature) {
        var rate = feature.data.unemployment_rate;
        var max_green = 255;
        var min_green = 1;
        var ceiling = 35;
        if (rate > ceiling) { setRGB( max_green )}
        var green = max_green - ((max_green - min_green) * (rate / ceiling))
        return setRGB(green);
    }
};

/* Firing up the map */
function load_map() {

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
    var style = new OpenLayers.Style({
        strokeColor : '#DDDDDD', 
        strokeWidth: 1,
        strokeOpacity: 0.4,
        fillColor : "${getColor}", 
        fillOpacity : 0.90, 
        pointRadius : 3,
        strokeLinecap: "round"
    }, { context: context });

    var styleMap = new OpenLayers.StyleMap({
        'default': style, 
        'select': new OpenLayers.Style({
            fillColor : "${getColor}",
            fillOpacity : 0.98,
            strokeWidth : 3,
            strokeOpacity: 0.90
            }, { context: context })
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
    var polygon_{{ object.county.id }} = wkt_f.read('{{ object.county.simple_polygon_900913 }}');
    polygon_{{ object.county.id }}.data = { 
        'unemployment_rate': {{ object.unemployment_rate }},
        'unemployment': "{{ object.unemployment|intcomma }}",
        'name': "{{ object.county.name }}"
        };
    {% endfor %}
    
    // Create a vector layer that will display all the data
    var county_vector = new OpenLayers.Layer.Vector("Counties");
    county_vector.styleMap = styleMap;
    // Then add all the polygons to the vector layer
    county_vector.addFeatures([{% for object in object_list %}polygon_{{ object.county.id }}{% if not forloop.last %}, {% endif %}{% endfor %}]);
    
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
                                "<div class='bubblewrap'><p class='county-hed'>" + feature.data.name + "</p><p style='margin-bottom:0px;'>Rate:&nbsp;" + feature.data.unemployment_rate + "%</p><p style='margin:0;'>" + "Total:&nbsp;" + feature.data.unemployment + "</p>" ,
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
                                "<p class='county-hed'>Thematic Map</strong>" +
                                "<p class='month-browse' style='margin:0;'><a href='{% url unemployment-month-detail month.year month.month %}?map=p'>Switch to proportional map &raquo;</a></p>" +
                                "</div>",
                                null, 
                                false, 
                                onPopupClose
                                );
    map.addPopup(key_popup)



};
