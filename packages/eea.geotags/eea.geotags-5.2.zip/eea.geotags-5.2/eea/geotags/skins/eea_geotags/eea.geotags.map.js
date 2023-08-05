jQuery(document).ready(function(){
    var djConfig = { parseOnLoad: true },
        url = "http://serverapi.arcgisonline.com/jsapi/arcgis/?v=2.8",
        map, map_options,
        portal_url = jQuery("#portal_url").html(),
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
    if(jQuery('#faceted-form').length) {
        jQuery(Faceted.Events).one('FACETED-AJAX-QUERY-SUCCESS', function(){
             if (jQuery("#map_points").length) {
                var portal_url = jQuery("#portal_url").html();
                map_options.featureCollectionRenderer.symbol.url = portal_url + "/event_icon.gif";
                map = jQuery('#eeaEsriMap');
                map.insertBefore("#content-core");
                jQuery.getScript(url, function () {
                    dojo.ready(function () {
                        map.EEAGeotagsView(map_options);
                    });
                });
                jQuery(Faceted.Events).bind('FACETED-AJAX-QUERY-SUCCESS', function(){
                    EEAGeotags.View.prototype.drawPoints();
                });
            }
        });
    }
    else {
        if (jQuery("#map_points").length) {
            map = jQuery("#eeaEsriMap");
            jQuery.getScript(url, function () {
                dojo.ready(function () {
                    map.EEAGeotagsView(map_options);
                });
            });
        }
    }
});
