map = new OpenLayers.Map("map");
var mainLayer = new OpenLayers.Layer.OSM(
        "New Layer",
        "http://b.tiles.mapbox.com/v3/dennisl.map-dfbkqsr2/${z}/${x}/${y}.png"
        );

map.addLayer(mainLayer);

epsg4326 = new OpenLayers.Projection("EPSG:4326"); //WGS 1984 projection
projectTo = map.getProjectionObject(); //The map projection (Spherical Mercator)

var vectorLayer = new OpenLayers.Layer.Vector("Overlay");
map.addLayer(vectorLayer);

var defaultZoom = 2;
map.setCenter(0, 0, defaultZoom);

function placeMarker(lat, lon) {
  var lonLat = new OpenLayers.LonLat(lon, lat).transform(epsg4326, projectTo);
  var point = new OpenLayers.Geometry.Point(lonLat.lon, lonLat.lat);
  var mycircle = OpenLayers.Geometry.Polygon.createRegularPolygon
  (
    point,
    321868.8, // Radius in meters (200 miles)
    40    // Number of sides
  );
  var marker = new OpenLayers.Feature.Vector(mycircle);
  vectorLayer.addFeatures(marker);
}

function updateMap() {
    jsonData = $('#users').bootstrapTable('getData');

    vectorLayer.removeAllFeatures();
    for(var i = 0; i < jsonData.length; i++) {
      lat = jsonData[i].latitude;
      lon = jsonData[i].longitude;

      if(lat !== undefined && lon !== undefined) {
        placeMarker(jsonData[i].latitude, jsonData[i].longitude);
      }
    }
}