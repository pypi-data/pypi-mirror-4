jQuery(document).ready(function($){
    window.djConfig = {parseOnLoad: true,
                    baseUrl: '.',
                    modulePaths: { 'EEAGeotags': '.' }
        };
    var url = "http://serverapi.arcgisonline.com/jsapi/arcgis/?v=2.8",
        map, map_options,
        portal_url = $("#portal_url").html(),
        feature_collection_renderer = {
            "type": "simple",
            "symbol": {
                "type": "esriPMS",
                "url": portal_url + "/event_icon.gif",
                "contentType": "image/gif",
                "width": 15,
                "height": 15
            }
        };
    map_options = {'infoWindowSize' : [350, 200], 'portalUrl': portal_url, 'featureCollectionRenderer': feature_collection_renderer};
    if($('#faceted-form').length) {
        $(window.Faceted.Events).one('FACETED-AJAX-QUERY-SUCCESS', function(){
             if ($("#map_points").length) {
                var portal_url = $("#portal_url").html(),
                    geotags_cluster_url = portal_url + '/geotagsClusterLayer.js';
                map_options.featureCollectionRenderer.symbol.url = portal_url + "/event_icon.gif";
                map_options.portalUrl = portal_url;
                map = $('#eeaEsriMap');
                map.insertBefore("#content-core");
                $.getScript(url, function () {
                    window.dojo.ready(function () {
                        $.getScript(geotags_cluster_url, function(res){
                            map.EEAGeotagsView(map_options);
                        });
                    });
                });
                $(window.Faceted.Events).bind('FACETED-AJAX-QUERY-SUCCESS', function(){
                    window.EEAGeotags.View.prototype.drawPoints();
                });
            }
        });
    }
    else {
        if ($("#map_points").length) {
            $.getScript(url, function () {
                window.dojo.ready(function () {
                    var geotags_cluster_url = portal_url + '/geotagsClusterLayer.js';
                    $.getScript(geotags_cluster_url, function(){
                        map = $("#eeaEsriMap");
                        map.EEAGeotagsView(map_options);
                    });
                });
            });
        }
    }
});
