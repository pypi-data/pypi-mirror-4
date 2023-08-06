/*global window, jQuery, google, dojo, esri, dijit*/

(function(){

jQuery.geoevents = {
  select_point: 'geo-event-select-point',
  select_marker: 'geo-event-select-marker',
  map_loaded: 'geo-events-map-loaded',
  basket_delete: 'geo-events-basket-delete',
  basket_save: 'geo-events-basket-save',
  ajax_start: 'geo-events-ajax-start',
  ajax_stop: 'geo-events-ajax-stop'
};

// Convert google geocoder to geojson
jQuery.google2geojson = function(googlejson){
  var feature = {
    type: 'Feature',
    bbox: [],
    geometry: {
      type: 'Point',
      coordinates: []
    },
    properties: {
      name: '',
      title: '',
      description: '',
      tags: '',
      center: [],
      other: googlejson
    }
  };
  feature.properties.title = googlejson.address_components[0].long_name;
  feature.properties.description = googlejson.formatted_address;
  feature.properties.tags = googlejson.types;

  // Geometry
  feature.properties.center = [
    googlejson.geometry.location.lat(),
    googlejson.geometry.location.lng()
  ];

  var bounds = googlejson.geometry.bounds;
  var type = 'Point';
  if(bounds){
    type = 'Polygon';
  }else{
    bounds = googlejson.geometry.viewport;
  }
  feature.geometry.type = type;

  var ne = bounds.getNorthEast();
  var sw = bounds.getSouthWest();
  if(type === 'Polygon'){
    feature.geometry.coordinates = [
      [sw.lat(), sw.lng()],
      [sw.lat(), ne.lng()],
      [ne.lat(), ne.lng()],
      [ne.lat(), sw.lng()]
    ];
  }else{
    feature.geometry.type = 'Point';
    feature.geometry.coordinates = [
      googlejson.geometry.location.lat(),
      googlejson.geometry.location.lng()
    ];
  }

  feature.bbox = [sw.lat(), sw.lng(), ne.lat(), ne.lng()];
  return feature;
};

/* Geolocator dialog jQuery plugin */
jQuery.fn.geodialog = function(settings){
  var self = this;
  self.initialized = false;
  self.events = {
    initialize: 'geo-dialog-initialize',
    save: 'geo-dialog-save'
  };

  self.options = {
    template: '',
    width: jQuery(window).width() * 0.85,
    height: jQuery(window).height() * 0.95,

    sidebar: {
      json: '',
      template: '',
      suggestions: '',
      fieldName: self.attr('id'),
      tabs: {
        search: {},
        advanced: {}
      }
    },

    map: {
      json: '',
      fieldName: self.attr('id')
    },

    basket: {
      json: '',
      template: '',
      fieldName: self.attr('id'),
      geojson: {
        type: 'FeatureCollection',
        features: []
      }
    },

    // Handlers
    handle_leftbutton_dblclick: function(button, area){
      var width = self.leftarea.width();
      var max_width = 300;
      var min_width = 0;
      if(width < 20){
        area.trigger('resize', [max_width]);
        jQuery('a', self.leftbutton).html('&laquo;');
      }else{
        area.trigger('resize', [min_width]);
        jQuery('a', self.leftbutton).html('&raquo;');
      }
    },

    handle_rightbutton_dblclick: function(button, area){
      var width = self.rightarea.width();
      var min_width = area.width();
      var max_width = parseInt(3 * area.width() / 4, 10);

      if(width < 20){
        area.trigger('resize', [max_width]);
        jQuery('a', self.rightbutton).html('&raquo;');
      }else{
        area.trigger('resize', [min_width]);
        jQuery('a', self.rightbutton).html('&laquo;');
      }
    },

    handle_initialize: function(data){
      if(self.initialized){
        // Already initialized
        return;
      }

      // Splitter
      jQuery.get(self.options.template, function(data){
        data = jQuery(data);
        self.empty();
        self.append(data);

        // Left splitter
        var left = jQuery('.geo-leftside', self);
        left.splitter({
          type: 'v',
          outline: true,
          accessKey: "L"
        });

        self.leftarea = jQuery('.geo-left', left);
        self.leftbutton = jQuery('.vsplitbar', left);
        jQuery('a', self.leftbutton).html('&raquo;');

        jQuery('a', self.leftbutton).click(function(){
          self.options.handle_leftbutton_dblclick(self.leftbutton, left);
        });

        self.leftbutton.dblclick(function(){
          self.options.handle_leftbutton_dblclick(self.leftbutton, left);
        });

        // Right splitter
        var right = jQuery('.geo-splitter', self);
        right.splitter({
          type: 'v',
          outline: true,
          sizeRight: 0,
          accessKey: "R"
        });

        self.rightarea = jQuery('.geo-right', right);
        self.rightbutton = jQuery(jQuery('.vsplitbar', right)[1]);
        jQuery('a', self.rightbutton).html('&laquo;');

        jQuery('a', self.rightbutton).click(function(){
          self.options.handle_rightbutton_dblclick(self.rightbutton, right);
        });

        self.rightbutton.dblclick(function(){
          self.options.handle_rightbutton_dblclick(self.rightbutton, right);
        });

        // Sidebar
        self.sidebar = jQuery('.geo-sidebar', self);
        self.sidebar.geosidebar(self.options.sidebar);

        // Map
        self.mapcanvas = jQuery('.geo-map', self);
        self.mapcanvas.geomap(self.options.map);

        // Basket
        self.basket = jQuery('.geo-basket', self);
        self.basket.geobasket(self.options.basket);
      });

      // Plugin initialized
      self.initialized = true;
    },

    handle_map_loaded: function(data){
      jQuery('a', self.leftbutton).click();
      jQuery('a', self.rightbutton).click();
    },

    handle_save: function(data){
      var fieldName = self.attr('id');
      var json = self.basket.options.geojson;
      // sort the geotags by name before sending it to object
      // annotation
      json.features = json.features.sort(function(a,b){
        var aName = a.properties.title.toLowerCase();
        var bName = b.properties.title.toLowerCase();
        return ((aName < bName) ? -1 : ((aName > bName) ? 1 : 0));
      });

      self.trigger(jQuery.geoevents.basket_save, {json: json});
      json = JSON.stringify(json);
      jQuery('[name=' + fieldName + ']').text(json);
    },

    initialize: function(){
      self.dialog({
        bgiframe: true,
        modal: true,
        closeOnEscape: false,
        autoOpen: false,
        width: self.options.width,
        height: self.options.height,
        resize: false,
        dialogClass: 'eea-geotags-popup',
        buttons: {
          'Done': function(){
            self.trigger(self.events.save);
            self.dialog('close');
          },
          'Cancel': function(){
            self.dialog('close');
          }
        },
        close: function(){
        },
        open: function(){
          self.trigger(self.events.initialize);
        }
      });

      // Bind events
      self.bind(self.events.initialize, function(evt, data){
        self.options.handle_initialize(data);
      });

      self.bind(self.events.save, function(evt, data){
        self.options.handle_save(data);
      });

      jQuery(self).bind(jQuery.geoevents.map_loaded, function(data){
        self.options.handle_map_loaded(data);
      });
    }
  };

  // Update settings
  if(settings){
    jQuery.extend(self.options, settings);
  }

  self.options.initialize();
  return this;
};

/* Geo Map Canvas jQuery plugin */
jQuery.fn.geomap = function(settings){
  var self = this;

  self.options = {
    json: '',
    fieldName: '',
    map_options : {
      latitude: 55,
      longitude: 35,
      center: null,
      zoom: 4,
      navigationControl: true,
      navigationControlOptions: {
        style: google.maps.NavigationControlStyle.ZOOM_PAN,
        position: google.maps.ControlPosition.RIGHT
      },
      mapTypeControl: true,
      mapTypeControlOptions: {
        position: google.maps.ControlPosition.TOP_RIGHT,
        style: google.maps.MapTypeControlStyle.DEFAULT
      },
      mapTypeId: google.maps.MapTypeId.TERRAIN
    },

    // Handlers
    handle_select: function(data, autoclick){
      if(!data){
        return;
      }

      if(data.bbox.length){
        var lat = data.bbox[0];
        var lng = data.bbox[1];
        var sw = new google.maps.LatLng(lat, lng);

        lat = data.bbox[2];
        lng = data.bbox[3];
        var ne = new google.maps.LatLng(lat, lng);

        var viewport = new google.maps.LatLngBounds(sw, ne);
        self.Map.fitBounds(viewport);
      }else{
        self.Map.setZoom(4);
      }

      // Marker
      jQuery.geomarker({
        fieldName: self.options.fieldName,
        map: self.Map,
        points: [data],
        center: data.properties.center,
        autoclick: autoclick
      });
    },

    handle_rightclick: function(data, center){
      // Markers
      jQuery.geomarker({
        fieldName: self.options.fieldName,
        map: self.Map,
        points: data.features,
        center: center
      });
    },

    initialize: function(){
      self.initialized = false;
      self.addClass('geo-mapcanvas');
      var options = self.options.map_options;
      if(!options.latlng){
        options.center = new google.maps.LatLng(
          options.latitude,
          options.longitude
        );
      }

      self.Map = new google.maps.Map(self[0], options);
      self.Geocoder = new google.maps.Geocoder();

      // Handle events
      var context = jQuery('#' + self.options.fieldName);
      jQuery(context).bind(jQuery.geoevents.select_point, function(evt, data){
        data.target.effect('transfer', {to: self}, 'slow', function(){
          self.options.handle_select(data.point, data.autoclick);
        });
      });

      // Map initialized
      google.maps.event.addListener(self.Map, 'tilesloaded', function(){
        if(self.initialized){
          return;
        }
        self.initialized = true;
        jQuery(context).trigger(jQuery.geoevents.map_loaded);
      });

      // Right click
      google.maps.event.addListener(self.Map, 'rightclick', function(data){
        var latlng = data.latLng;
        var center = [latlng.lat(), latlng.lng()];

        // Empty marker to clear map
        jQuery.geomarker({
          fieldName: self.options.fieldName,
          map: self.Map,
          center: center,
          points: []
        });

        jQuery(context).trigger(jQuery.geoevents.ajax_start);
        self.Geocoder.geocode({location: latlng}, function(results){
          var features = [];
          jQuery.each(results, function(){
            features.push(jQuery.google2geojson(this));
          });

          results = {
            type: 'FeatureCollection',
            features: features
          };

          self.options.handle_rightclick(results, center);
          jQuery(context).trigger(jQuery.geoevents.ajax_stop);
        });
      });
    }
  };

  if(settings){
    jQuery.extend(self.options, settings);
  }

  // Return
  self.options.initialize();
  return this;
};

jQuery.geomarker = function(settings){
  var self = this;

  self.options = {
    fieldName: '',
    template: '<div class="geo-marker">' +
                '<h3 class="title"></h3>' +
                '<h4 class="subtitle"></h4>' +
                '<h5 class="tags"></h5>' +
              '</div>',
    map: null,
    points: [],
    center: [0, 0],
    autoclick:false,

    initialize: function(){
      self.options.clear();
      self.mappoints = {};

      // Marker
      var center = self.options.center;
      var latlng = new google.maps.LatLng(center[0], center[1]);
      self.marker = new google.maps.Marker({
        position: latlng
      });
      self.marker.setMap(self.options.map);

      // InfoWindow
      var template = jQuery('<div>');
      jQuery.each(self.options.points, function(){
        var point = this;
        var uid = point.properties.center[0] + '-' + point.properties.center[1];
        self.mappoints[uid] = point;

        var title = this.properties.title;
        var subtitle = this.properties.description;
        var tags = '';
        if(typeof(this.properties.tags) === 'string'){
          tags = this.properties.tags;
        }else{
          jQuery.each(this.properties.tags, function(){
            tags += this + ', ';
          });
        }

        var itemplate = jQuery(self.options.template);
        itemplate.attr('id', uid).attr('title', 'Add');
        var icon = jQuery('<div>')
          .addClass('ui-icon')
          .addClass('ui-icon-extlink')
          .text('+');
        itemplate.prepend(icon);
        jQuery('.title', itemplate).text(title);
        jQuery('.subtitle', itemplate).text(subtitle);
        jQuery('.tags', itemplate).text(tags);

        template.append(itemplate);
      });

      var context = jQuery('#' + self.options.fieldName);
      if(self.options.points.length){
        // Add info window
        self.info = new google.maps.InfoWindow({
          content: template.html()
        });

        self.info.open(self.options.map, self.marker);
        google.maps.event.addListener(self.info, 'domready', function(){
          jQuery('.geo-marker').click(function(){
            var _self = jQuery(this);
            jQuery(context).trigger(jQuery.geoevents.select_marker, {
              point: self.mappoints[_self.attr('id')],
              button: _self
            });
          });

          // Autoclick
          if(self.options.autoclick){
            jQuery('.geo-marker').click();
          }
        });

        // Google event handlers
        google.maps.event.addListener(self.marker, 'click', function() {
          self.info.open(self.options.map, self.marker);
        });
      }
    },

    clear: function(){
      if(self.marker){
        self.marker.setMap(null);
      }
      if(self.info){
        self.info.close();
      }
    }
  };

  if(settings){
    jQuery.extend(self.options, settings);
  }

  self.options.initialize();
  return this;
};

/* Geo basket jQuery plugin */
jQuery.fn.geobasket = function(settings){
  var self = this;

  self.options = {
    json: '',
    template: '',
    fieldName: '',
    multiline: 1,
    geojson: {
      type: 'FeatureCollection',
      features: []
    },

    initialize: function(){
      var query = {};
      query.fieldName = self.options.fieldName;
      jQuery.get(self.options.template, query, function(data){
        self.html(data);
        self.options.redraw(false);
      });

      var context = jQuery('#' + self.options.fieldName);
      jQuery(context).bind(jQuery.geoevents.select_marker, function(evt, data){
        data.button.effect('transfer', {to: self}, 'slow', function(){
          self.options.handle_select(data.point);
        });
      });

      jQuery(context).bind(jQuery.geoevents.basket_delete, function(evt, data){
        data.element.slideUp(function(){
          jQuery(this).remove();
          self.options.handle_delete(data.point);
        });
      });
    },

    handle_delete: function(point){
      var pcenter = point.properties.center;
      pcenter = pcenter[0] + '-' + pcenter[1];
      self.options.geojson.features = jQuery.map(self.options.geojson.features,
        function(feature, index){
          var center = feature.properties.center;
          center = center[0] + '-' + center[1];
          if(pcenter !== center){
            return feature;
          }
      });
    },

    handle_select: function(point){
      var i, initialData = window.EEAGeotags.initialCountryData,
           initialData_length, names, features_length;
      if(!self.options.multiline){
        self.options.geojson.features = [];
      }else{
        self.options.handle_delete(point);
      }

      if (initialData) {
        names = [];
        // add also the individual countries that are part of this country group
        initialData_length = initialData.features.length;
        features_length = self.options.geojson.features.length; 
        for (i = 0; i < features_length; i += 1) {
            names.push(self.options.geojson.features[i].properties.name);
        }
        for (i = 0; i < initialData_length; i += 1) {
            // add only the countries that are not already in the list by checking
            // their geotags name
            if (jQuery.inArray(initialData.features[i].properties.name, names) === -1) {
                self.options.geojson.features.unshift(initialData.features[i]);
            }
        }
      }
      else {
        self.options.geojson.features.unshift(point);
      }
      self.options.redraw(true);
    },

    redraw: function(highlight){
      var items = jQuery('.geo-basket-items', self);
      items.empty();

      jQuery.each(self.options.geojson.features, function(){
        var div = jQuery('<div>');
        items.append(div);
        div.geobasketitem({
          fieldName: self.options.fieldName,
          point: this
        });
      });
      if(highlight){
        var first = jQuery('.geo-point-view:first', items);
        first.addClass('ui-pulsate-item');
        first.effect('pulsate', {}, 200, function(){
          first.removeClass('ui-pulsate-item');
        });
      }
    }
  };

  if(settings){
    jQuery.extend(self.options, settings);
  }

  // Return
  self.options.initialize();
  return this;
};

/* Geo basket item */
jQuery.fn.geobasketitem = function(settings){
  var self = this;
  self.options = {
    fieldName: '',
    template: '<div>' +
                '<h3 class="title"></h3>' +
                '<h4 class="subtitle"></h4>' +
                '<h5 class="tags"></h5>' +
              '</div>',
    point: {},

    // Methods
    initialize: function(){
      self.addClass('geo-point-view');
      self.delbutton = jQuery('<div>')
        .addClass('ui-icon')
        .addClass(' ui-icon-trash')
        .text('X')
        .attr('title', 'Delete');
      self.prepend(self.delbutton);

      var context = jQuery('#' + self.options.fieldName);
      self.delbutton.click(function(){
        jQuery(context).trigger(jQuery.geoevents.basket_delete, {
          point: self.options.point,
          element: self
        });
      });

      var title = self.options.point.properties.title;
      var subtitle = self.options.point.properties.description;
      var tags = '';
      if(typeof(self.options.point.properties.tags) === 'string'){
        tags = self.options.point.properties.tags;
      }else{
        jQuery.each(self.options.point.properties.tags, function(){
          tags += this + ', ';
        });
      }

      var template = jQuery(self.options.template);
      jQuery('.title', template).text(title);
      jQuery('.subtitle', template).text(subtitle);
      jQuery('.tags', template).text(tags);

      self.append(template);
    }
  };

  if(settings){
    jQuery.extend(self.options, settings);
  }

  self.options.initialize();
  return this;
};

/* Geo Side bar jQuery plugin */
jQuery.fn.geosidebar = function(settings){
  var self = this;
  self.options = {
    json: '',
    template: '',
    suggestions: '',
    fieldName: '',
    tabs: {
      search: {},
      advanced: {}
    },

    // Methods
    initialize: function(){
      var query = {};
      query.fieldName = self.options.fieldName;
      jQuery.get(self.options.template, query, function(data){
        self.sidebararea = jQuery(data);

        self.loading = jQuery('<div>');
        self.sidebararea.append(self.loading);
        self.loading.geoloader({
          fieldName: self.options.fieldName
        });

        self.append(self.sidebararea);

        var options = self.options.tabs;
        options.json = self.options.json;
        options.fieldName = self.options.fieldName;
        options.suggestions = self.options.suggestions;
        self.sidebararea.geotabs(options);
      });
    }

  };

  if(settings){
    jQuery.extend(self.options, settings);
  }

  self.options.initialize();
  return this;
};

jQuery.fn.geoloader = function(settings){
  var self = this;
  self.working = 0;

  self.options = {
    fieldName: '',

    initialize: function(){
      self.addClass('geo-loading');
      self.hide();

      var context = jQuery('#' + self.options.fieldName);
      self.ajaxStart(function(){
        jQuery(context).trigger(jQuery.geoevents.ajax_start);
      });

      self.ajaxStop(function(){
        jQuery(context).trigger(jQuery.geoevents.ajax_stop);

      });

      jQuery(context).bind(jQuery.geoevents.ajax_start, function(){
        self.show();
      });

      jQuery(context).bind(jQuery.geoevents.ajax_stop, function(){
        self.hide();
      });
    },

    show: function(){
      self.working += 1;
      if(self.working > 0){
        self.show();
      }
    },

    hide: function(){
      self.working -= 1;
      if(!self.working){
        self.hide();
      }
    }
  };


  if(settings){
    jQuery.extend(self.options, settings);
  }

  self.options.initialize();
  return this;
};

/* Geo tabs jQuery plugin */
jQuery.fn.geotabs = function(settings){
  var self = this;

  self.options = {
    json: '',
    fieldName: '',
    suggestions: '',
    search: {},
    advanced: {},

    // Methods
    initialize: function(){
      jQuery('ul.geo-tabs', self).tabs('div.geo-panes > div');
      var options = self.options.search;
      options.json = self.options.json;
      options.fieldName = self.options.fieldName;
      options.suggestions = self.options.suggestions;
      jQuery('.geo-results', self).geosearchtab(options);

      options = self.options.advanced;
      options.json = self.options.json;
      options.fieldName = self.options.fieldName;
      jQuery('.geo-advanced', self).geoadvancedtab(options);

    }
  };

  if(settings){
    jQuery.extend(self.options, settings);
  }

  self.options.initialize();
  return this;
};

/* Geo search tab jQuery plugin */
jQuery.fn.geosearchtab = function(settings){
  var self = this;

  // Default settings
  self.options = {
    // Settings
    fieldName: '',
    json: '',
    suggestions: '',
    query: {
      address: '',
      q: '',
      maxRows: 10
    },

    handle_suggestions: function(data){
      var suggestions = data.suggestions;

      if(!suggestions.length){
        return;
      }

      var htitle = jQuery('<h5>').text('Suggestions').addClass('geo-suggestions');
      self.resultsarea.append(htitle);

      var context = jQuery('#' + self.options.fieldName);

      jQuery.each(suggestions, function(){
        self.options.query.address = this.text;
        jQuery(context).trigger(jQuery.geoevents.ajax_start);
        var xquery = {'address': this.text};
        self.Geocoder.geocode(xquery, function(data){
          var features = [];
          jQuery.each(data, function(){
            features.push(jQuery.google2geojson(this));
          });

          var geojson = {
            type: 'FeatureCollection',
            features: features
          };

          self.options.handle_query(geojson, false);
          jQuery(context).trigger(jQuery.geoevents.ajax_stop);
        });
      });
    },

    // Handlers
    handle_submit: function(){
      self.searchbutton.removeClass('submitting');

      var value = self.searchtext.val();
      if(!value || (value === self.options.query.address)){
        return;
      }

      self.options.query.address = value;
      self.options.query.q = value;
      var query = self.options.query;

      var context = jQuery('#' + self.options.fieldName);
      jQuery(context).trigger(jQuery.geoevents.ajax_start);

      // Search with geonames.org
      jQuery.getJSON(self.options.json, query, function(data){
        if(data.features.length){
          self.options.handle_query(data, true);
          jQuery(context).trigger(jQuery.geoevents.ajax_stop);
        }else{
        // Search with Google
          var xquery = {address: query.address};
          self.Geocoder.geocode(xquery, function(data){
            var features = [];
            jQuery.each(data, function(){
              features.push(jQuery.google2geojson(this));
            });

            data = {
              type: 'FeatureCollection',
              features: features
            };

            self.options.handle_query(data, true);
            jQuery(context).trigger(jQuery.geoevents.ajax_stop);
          });
        }
      });
    },

    handle_query: function(data, reset){
      self.results = data;
      if(reset){
        self.resultsarea.empty();

        if(!self.results.features.length){
          var div = jQuery('<div>').addClass('geo-hints');
          div.text('We could not find a match for this location anywhere. ' +
          'Please check your spelling or try looking for a different location.');
          self.resultsarea.append(div);
          return;
        }
      }

      jQuery.each(self.results.features, function(){
        var div = jQuery('<div>');
        div.geopointview({
          fieldName: self.options.fieldName,
          point: this
        });
        self.resultsarea.append(div);
      });
    },

    // Initialize
    initialize: function(){
      self.searchform = jQuery('form', self);
      self.searchbutton = jQuery('input[type=submit]', self.searchform);
      self.searchtext = jQuery('input[type=text]', self.searchform);
      self.resultsarea = jQuery('.geo-results-area', self);

      self.Geocoder = new google.maps.Geocoder();

      // Handle suggestions
      if(self.options.suggestions.length){
        jQuery.getJSON(self.options.suggestions, {}, function(data){
          self.options.handle_suggestions(data);
        });
      }

      self.searchform.submit(function(){
        self.options.handle_submit();
        return false;
      });

    }
  };

  // Update settings
  if(settings){
    jQuery.extend(self.options, settings);
  }

  self.options.initialize();
  return this;
};

/* Geo point view jQuery plugin */
jQuery.fn.geopointview = function(settings){
  var self = this;
  self.options = {
    fieldName: '',
    template: '<div>' +
                '<h3 class="title"></h3>' +
                '<h4 class="subtitle"></h4>' +
                '<h5 class="tags"></h5>' +
              '</div>',
    point: {},

    // Methods
    initialize: function(){
      self.addClass('geo-point-view').attr('title', 'See on map');
      var icon = jQuery('<div>')
        .addClass('ui-icon')
        .addClass('ui-icon-extlink')
        .text('+');
      self.prepend(icon);

      var title = self.options.point.properties.title;
      var subtitle = self.options.point.properties.description;
      var tags = '';
      if(typeof(self.options.point.properties.tags) === 'string'){
        tags = self.options.point.properties.tags;
      }else{
        jQuery.each(self.options.point.properties.tags, function(){
          tags += this + ', ';
        });
      }

      var template = jQuery(self.options.template);
      jQuery('.title', template).text(title);
      jQuery('.subtitle', template).text(subtitle);
      jQuery('.tags', template).text(tags);

      self.append(template);

      var context = jQuery('#' + self.options.fieldName);
      self.click(function(){
        jQuery(context).trigger(jQuery.geoevents.select_point, {
          point: self.options.point,
          target: self,
          autoclick: true
        });
      });
    }

  };

  if(settings){
    jQuery.extend(self.options, settings);
  }

  // Return
  self.options.initialize();
  return this;
};

/* Geo advanced tab jQuery plugin */
jQuery.fn.geoadvancedtab = function(settings){
  var self = this;
  self.options = {
    fieldName: '',
    json: '',

    // Methods
    handle_biogroups_change: function(){
      var value = self.biogroups.val();

      if(!value){
        return;
      }

      var value_json = {};
      jQuery.each(self.biogroups.geojson.features, function(){
        if(this.properties.name === value){
          value_json = this;
          return false;
        }
      });

      var context = jQuery('#' + self.options.fieldName);
      jQuery(context).trigger(jQuery.geoevents.select_point, {
        point: value_json,
        target: self.biogroups
      });
    },

    handle_groups_change_reset: function(){
      self.countries.empty().parent().hide();
      self.nuts.empty().parent().hide();
      self.cities.empty().parent().hide();
      self.naturalfeatures.empty().parent().hide();
    },

    handle_groups_change: function(){
      self.options.handle_groups_change_reset();

      var value = self.groups.val();
      if(!value){
        return;
      }

      var value_json = {};
      jQuery.each(self.data.features, function(){
        if(this.properties.name === value){
          value_json = this;
          return false;
        }
      });

      var context = jQuery('#' + self.options.fieldName);

      // Get countries
      jQuery.getJSON(self.options.json, {
        type: 'countries', group: value}, function(data){
        // save initial country data to be used when adding country groups
        if ($("#expand_countries").is(':checked')) {
            window.EEAGeotags.initialCountryData = data;
        }

        self.countries.empty();
        var option = jQuery('<option>').val('').text('');
        self.countries.append(option);

        jQuery.each(data.features, function(index){
          // Center map on second country in group
          if(index === 1){
            value_json.properties.center = this.properties.center;
            jQuery(context).trigger(jQuery.geoevents.select_point, {
              point: value_json,
              target: self.groups
            });
          }
          // Add countries to datamodel
          if(value_json.properties.countries === undefined){
            value_json.properties.countries = [];
          }
          value_json.properties.countries.push(this.properties.title);

          option = jQuery('<option>')
            .val(this.properties.name)
            .text(this.properties.title)
            .data('geojson', this);
          self.countries.append(option);
        });

        self.countries.parent().show();
      });
    },

    handle_countries_change_reset: function(){
      self.nuts.empty().parent().hide();
      self.cities.empty().parent().hide();
      self.naturalfeatures.empty().parent().hide();
    },

    handle_countries_change: function(){
      self.options.handle_countries_change_reset();

      var country = jQuery('option:selected', self.countries);

      if(!country.length){
        return;
      }

      // Center map
      var query = {
        address: country.data('geojson').properties.title,
        region: country.data('geojson').properties.country
      };

      var context = jQuery('#' + self.options.fieldName);
      self.Geocoder.geocode(query, function(data){
        if(!data.length){
          return;
        }

        data = jQuery.google2geojson(data[0]);
        jQuery(context).trigger(jQuery.geoevents.select_point, {
          point: data,
          target: self.countries
        });
      });

      // Get nut regions
      jQuery.getJSON(self.options.json, {
        type: 'nuts', country: query.region}, function(data){
        self.nuts.empty();
        var option = jQuery('<option>').val('').text('');
        self.nuts.append(option);
        jQuery.each(data.features, function(){
          option = jQuery('<option>')
            .val(this.properties.name)
            .text(this.properties.title)
            .data('geojson', this);
          self.nuts.append(option);
        });
        self.nuts.parent().show();
      });

      // Get natural features
      jQuery.getJSON(self.options.json, {
        type: 'natural', country: query.region}, function(data){
        self.naturalfeatures.empty();
        var option = jQuery('<option>').val('').text('');
        self.naturalfeatures.append(option);
        jQuery.each(data.features, function(){
          option = jQuery('<option>')
            .val(this.properties.name)
            .text(this.properties.title)
            .data('geojson', this);
          self.naturalfeatures.append(option);
        });
        self.naturalfeatures.parent().show();
      });

    },

    handle_nuts_change_reset: function(){
      self.cities.empty().parent().hide();
    },

    handle_nuts_change: function(){
      self.options.handle_nuts_change_reset();

      var nut = jQuery('option:selected', self.nuts);
      if(!nut.length){
        return;
      }

      var query = {
        address: nut.data('geojson').properties.adminName1,
        region: nut.data('geojson').properties.country
      };

      var context = jQuery('#' + self.options.fieldName);
      // Center map
      self.Geocoder.geocode(query, function(data){
        if(!data.length){
          return;
        }

        data = jQuery.google2geojson(data[0]);
        jQuery(context).trigger(jQuery.geoevents.select_point, {
          point: data,
          target: self.nuts
        });
      });

      // Get cities
      var req = {
        type: 'cities',
        country: query.region,
        adminCode1: nut.data('geojson').properties.adminCode1
      };

      jQuery.getJSON(self.options.json, req, function(data){
        self.cities.empty();
        var option = jQuery('<option>').val('').text('');
        self.cities.append(option);
        jQuery.each(data.features, function(){
          option = jQuery('<option>')
            .val(this.properties.name)
            .text(this.properties.title)
            .data('geojson', this);
          self.cities.append(option);
        });
        self.cities.parent().show();
      });

      //. Get natural features
      var req_natural = {
        type: 'natural',
        country: req.country,
        adminCode1: req.adminCode1
      };

      jQuery.getJSON(self.options.json, req_natural, function(data){
        self.naturalfeatures.empty();
        var option = jQuery('<option>').val('').text('');
        self.naturalfeatures.append(option);
        jQuery.each(data.features, function(){
          option = jQuery('<option>')
            .val(this.properties.name)
            .text(this.properties.title)
            .data('geojson', this);
          self.naturalfeatures.append(option);
        });
        self.naturalfeatures.parent().show();
      });

    },

    handle_cities_change: function(){
      var city = jQuery('option:selected', self.cities);
      if(!city.length){
        return;
      }

      // Center map
      var query = {
        address: city.data('geojson').properties.title + ', ' +
                 city.data('geojson').properties.adminName1,
        region: city.data('geojson').properties.country
      };

      var context = jQuery('#' + self.options.fieldName);
      self.Geocoder.geocode(query, function(data){
        if(!data.length){
          return;
        }

        data = jQuery.google2geojson(data[0]);
        jQuery(context).trigger(jQuery.geoevents.select_point, {
          point: data,
          target: self.cities
        });
      });
    },

    handle_naturalfeatures_change: function(){
      var natural = jQuery('option:selected', self.naturalfeatures);
      if(!natural.length){
        return;
      }

      // Center map
      var query = {
        address: natural.data('geojson').properties.title + ', ' +
                 natural.data('geojson').properties.adminName1,
        region: natural.data('geojson').properties.country
      };

      var context = jQuery('#' + self.options.fieldName);
      self.Geocoder.geocode(query, function(data){
        if(!data.length){
          return;
        }

        data = jQuery.google2geojson(data[0]);
        jQuery(context).trigger(jQuery.geoevents.select_point, {
          point: data,
          target: self.naturalfeatures
        });
      });
    },

    // Initialize
    initialize: function(){
      self.biogroups = jQuery('select[name=biogroups]', self);
      self.groups = jQuery('select[name=groups]', self);
      self.countries = jQuery('select[name=countries]', self);
      self.nuts = jQuery('select[name=nuts]', self);
      self.cities = jQuery('select[name=cities]', self);
      self.naturalfeatures = jQuery('select[name=naturalfeature]', self);
      self.data = {};

      self.Geocoder = new google.maps.Geocoder();

      // Hide
      self.countries.parent().hide();
      self.nuts.parent().hide();
      self.cities.parent().hide();
      self.naturalfeatures.parent().hide();

      // Fill biogeographical regions
      jQuery.getJSON(self.options.json, {type: 'biogroups'}, function(data){
        self.biogroups.empty();
        var option = jQuery('<option>').val('').text('');
        self.biogroups.append(option);
        jQuery.each(data.features, function(){
          self.biogroups.geojson = data;
          option = jQuery('<option>')
            .val(this.properties.name)
            .text(this.properties.title);
          self.biogroups.append(option);
        });
      });

      // Fill groups
      jQuery.getJSON(self.options.json, {type: 'groups'}, function(data){
        self.data = data;
        self.groups.empty();
        var option = jQuery('<option>').val('').text('');
        self.groups.append(option);
        jQuery.each(self.data.features, function(){
          option = jQuery('<option>')
            .val(this.properties.name)
            .text(this.properties.title);
          self.groups.append(option);
        });
      });

      // Events
      self.biogroups.change(function(){
        self.options.handle_biogroups_change();
      });

      self.groups.change(function(){
        self.options.handle_groups_change();
      });

      self.countries.change(function(){
        self.options.handle_countries_change();
      });

      self.nuts.change(function(){
        self.options.handle_nuts_change();
      });

      self.cities.change(function(){
        self.options.handle_cities_change();
      });

      self.naturalfeatures.change(function(){
        self.options.handle_naturalfeatures_change();
      });
    }
  };

  if(settings){
    jQuery.extend(self.options, settings);
  }

  // Return
  self.options.initialize();
  return this;
};

jQuery.fn.geopreview = function(settings){
  var self = this;
  self.options = {
    json: {},
    fieldName: '',
    template: '<div><div class="geo-preview-marker">' +
                '<h3 class="title"></h3>' +
                '<h4 class="subtitle"></h4>' +
                '<h5 class="tags"></h5>' +
              '</div></div>',
    map_options : {
      latitude: 55,
      longitude: 35,
      center: null,
      zoom: 3,
      navigationControl: true,
      navigationControlOptions: {
        style: google.maps.NavigationControlStyle.ZOOM_PAN
//        position: google.maps.ControlPosition.RIGHT // this generated a javascript error in IE
      },
      mapTypeControl: true,
      mapTypeControlOptions: {
        position: google.maps.ControlPosition.TOP_RIGHT,
        style: google.maps.MapTypeControlStyle.DEFAULT
      },
      mapTypeId: google.maps.MapTypeId.TERRAIN
    },

    handle_points: function(json){
      self.options.handle_cleanup();
      if(!json.features){
        return;
      }

      jQuery.each(json.features, function(){
        var center = this.properties.center;
        var latlng = new google.maps.LatLng(center[0], center[1]);
        var marker = new google.maps.Marker({
          position: latlng
        });
        marker.setMap(self.Map);
        self.markers.push(marker);

        var title = this.properties.title;
        var subtitle = this.properties.description;
        var tags = '';
        if(typeof(this.properties.tags) === 'string'){
          tags = this.properties.tags;
        }else{
          jQuery.each(this.properties.tags, function(){
            tags += this + ', ';
          });
        }

        var itemplate = jQuery(self.options.template);
        jQuery('.title', itemplate).text(title);
        jQuery('.subtitle', itemplate).text(subtitle);
        jQuery('.tags', itemplate).text(tags);

        // Google event handlers
        google.maps.event.addListener(marker, 'click', function() {
          self.info.setContent(itemplate.html());
          self.info.open(self.Map, marker);
        });
      });
    },

    handle_cleanup: function(){
     jQuery.each(self.markers, function(){
        this.setMap(null);
      });
      self.markers.length = 0;

      if(self.info){
        self.info.close();
      }
    },

    initialize: function(){
      self.markers = [];
      self.info = new google.maps.InfoWindow({
        content: ''
      });

      self.addClass('geo-preview-mapcanvas');
      var options = self.options.map_options;
      if(!options.latlng){
        options.center = new google.maps.LatLng(
          options.latitude,
          options.longitude
        );
      }

      self.Map = new google.maps.Map(self[0], options);
      self.Geocoder = new google.maps.Geocoder();

      self.options.handle_points(self.options.json);
      var context = jQuery('#' + self.options.fieldName);
      context.bind(jQuery.geoevents.basket_save, function(evt, data){
        self.options.handle_points(data.json);
      });

      // Fix preview map
      jQuery('form[name=edit_form] .formTab, .wizard-left, .wizard-right').click(function(){
        // #5339 fix preview map also when using eea.forms
        if(jQuery(this).closest('form').find('.formPanel:visible').find('#location-geopreview').length){
            google.maps.event.trigger(self.Map, 'resize');
            self.Map.setCenter(options.center);
            self.Map.setZoom(options.zoom);
        }
      });
    }
  };

  if(settings){
    jQuery.extend(self.options, settings);
  }

  // Return
  self.options.initialize();
  return this;
};

// End namespace
}());


if(window.EEAGeotags === undefined){
  var EEAGeotags = {'version': '1.0'};
}

// EEA Geotags view widget on map
EEAGeotags.View = function(context, options){
  var self = this;
  self.map = '';
  self.context = context;
  self.context.parent().addClass('eea-geotags-view');
  self.settings = {};

  if(options){
    jQuery.extend(self.settings, options);
  }
  EEAGeotags.settings = self.settings;
  self.initialize();
};

EEAGeotags.View.prototype = {

  initialize: function(){
    var self = this;
    dojo.require('dijit.layout.BorderContainer');
    dojo.require('dijit.layout.ContentPane');
    dojo.require('esri.map');
    dojo.require('esri.dijit.Scalebar');
    dojo.require("esri.layers.FeatureLayer");
    dojo.require("esri.dijit.Popup");
    dojo.require("GeotagsClusterLayer");
    self.init();
  },

  init: function(){
    var self = this,
        eea_location = jQuery('.eea-location-listing'),
        eea_location_links = eea_location.find('a'),
        eea_location_links_length = eea_location_links.length;
        self.modal = eea_location_links_length  ? eea_location.data().modal : "Events";
        self.map_div = jQuery("#eeaEsriMap");
    if( (self.modal !== "False" && self.modal !== "Events") || (eea_location_links_length < 4 && self.modal !== "Events")){
        var dialogBox,
            eea_location_offset = eea_location.offset(),
            pos_top = eea_location_offset.top + eea_location.height(),
            pos_left = jQuery("#content").offset().left,
            body = jQuery('html, body'),
            content_width = jQuery("#content").width();
            // CREATE MAP
            self.map_div.show();
            self.initMap(eea_location_links);
            self.map_div.hide();
        eea_location_links.click(function(e){
            if (!dialogBox) {
                body.animate({scrollTop: pos_top - 80 }, 400);
                // ie bug which fails if we have open and width and height in
                // the dialog options so we add then with plain jquery css
                dialogBox = self.map_div.dialog({autoOpen : false});
                dialogBox.closest('.ui-dialog').css({left: pos_left, top: pos_top, display: 'block', width: content_width - 6, height: 450});
                // resize map root to fit the designated space of #content
                // without scrollbars
                self.map_div.find('#eeaEsriMap_root').css({width: '100%', height: '100%'});

            }
            else {
                body.animate({scrollTop: pos_top - 80 }, 400);
                dialogBox.closest('.ui-dialog').css({left: pos_left, top: pos_top, display: 'block'});
            }
            e.preventDefault();
        });
    }
    else {
        self.map_div.show(); //.css('opacity', 0);
        self.initMap(eea_location_links);
    }
  },
  // Show loading image
  showLoading: function(){
    var loading;
    var self = this;
    loading = jQuery('#eeaEsriMapLoadingImg')[0];
    esri.show(loading);
    self.disableMapNavigation();
    self.hideZoomSlider();
  },

  // Hide loading image
  hideLoading: function(){
    var loading;
    var self = this;
    loading = jQuery('#eeaEsriMapLoadingImg')[0];
    esri.hide(loading);
    self.enableMapNavigation();
    self.showZoomSlider();
  },

  // Draw points on map
  drawPoints: function(eea_location_links){
    var self = this,
        context_url, infoSymbol, infoTemplate, map_points, locationTags, locationTagsLen;
    map_points = jQuery('#map_points');
    locationTags = eea_location_links;
    locationTagsLen = locationTags ? locationTags.length : 0;

    context_url = window.location.protocol + '//' + window.location.host + window.location.pathname;

    infoSymbol = new esri.symbol.SimpleMarkerSymbol().setSize(10).setColor(new dojo.Color('#B1C748'));
    var infotemplate = map_points.length ? '<h3>${Title}</h3><img src="${Url}/image_thumb" class="esriInfoImg" />': '${Addr}';
    infoTemplate = new esri.InfoTemplate('${Name}', infotemplate);
    EEAGeotags.map.infoWindow.hide();
    var featureCollection = {
        "layerDefinition": null,
        "featureSet": {
        "features": [],
        "geometryType": "esriGeometryPoint"
        }
    };
    var renderer;
    var portal = EEAGeotags.settings.portal_url + "/" || "/";
    if(self.modal === "Events") {
       renderer =
        {
            "type": "simple",
            "symbol": {
                "type": "esriPMS",
                "url": portal + EEAGeotags.settings.infoWindowImgName,
                "width": 15,
                "height": 15
            }
        };
    }
    featureCollection.layerDefinition = {
        "geometryType": "esriGeometryPoint",
        "objectIdField": "ObjectID",
        "drawingInfo": {
        "renderer": EEAGeotags.settings.featureCollectionRenderer || renderer
        },
        "fields": [{
        "name": "ObjectID",
        "alias": "ObjectID",
        "type": "esriFieldTypeOID"
        },{
        "name": "description",
        "alias": "Description",
        "type": "esriFieldTypeString"
        },{
        "name": "title",
        "alias": "Title",
        "type": "esriFieldTypeString"
        }]
    };

    // remove previous graphics before adding new ones with faceted navigation
    // queries
    if(EEAGeotags.featureLayer) {
        EEAGeotags.featureLayer.clear();
    }
    var setPoints = function(res, results){
        //define a popup template
        var popup = new esri.dijit.Popup(null, dojo.create("div"));
           EEAGeotags.map.setInfoWindow(popup);
        var popupTemplate = new esri.dijit.PopupTemplate({
          title: "{title}",
          description:"{description}"
        });
        //create a feature layer based on the feature collection
        var featureLayer = new esri.layers.FeatureLayer(res, {
          id: 'geotagsLayer',
          infoTemplate: popupTemplate
        });


        // add or change read more link for pop-up
        dojo.connect(popup,"onSelectionChange",function(){
            var feature = popup.getSelectedFeature();
            var readmeLink = dojo.query(".readmore", EEAGeotags.map.infoWindow.domNode)[0];
                if(feature && feature.attributes.Url) {
                    if (!readmeLink) {
                        dojo.create("a", {
                            "class": "action readmore",
                            "innerHTML": "Read More",
                            "href": feature.attributes.Url
                        }, dojo.query(".actionList", EEAGeotags.map.infoWindow.domNode)[0]);
                    }
                    else {
                        readmeLink.href = feature.attributes.Url;
                    }
                }
        });

        //associate the features with the popup on click
        dojo.connect(featureLayer,"onClick",function(evt){
            var features = [];
            dojo.forEach(featureLayer.graphics, function(item) {
                if (evt.graphic.geometry.x === item.geometry.x) {
                        features.push(item);
                }
            });
            popup.hide();
            EEAGeotags.map.infoWindow.setFeatures(features);
        });

        var features = [];
        var initialTemplate = infoTemplate.content,
            tempTemplate = "";
        var wgs = new esri.SpatialReference({ "wkid": 102100 });
        jQuery.each(results, function (i, item) {
            var geometry, mapPoint, attributes;
            geometry = new esri.geometry.Point(parseFloat(item.properties.center[1]), parseFloat(item.properties.center[0]), wgs);
            geometry = esri.geometry.geographicToWebMercator(geometry);
            var name = item.itemType || 'Location',
                itemUrl = item.itemUrl || context_url,
                icon = item.itemIcon || itemUrl + '/image_listing',
                addr = decodeURIComponent(item.properties.description) || decodeURIComponent(item.properties.title),
                itemDate = item.itemDate,
                itemDescription = item.itemDescription,
                mapOptions = {'Name' : name,
                              'Url' : item.itemUrl,
                              'Title': decodeURIComponent(item.itemTitle)};

            // add extra template information only if it's available from the catalog search
            tempTemplate = initialTemplate;

            if (addr) {
                tempTemplate = tempTemplate + '<p><strong>Location: </strong>${Addr}</p>';
                mapOptions.Addr = addr;
            }
            if (itemDate && parseInt(itemDate, 10)) {
                tempTemplate = tempTemplate + '<p><strong>Period: </strong>${Period}</p>';
                mapOptions.Period = itemDate;
            }
            if (itemDescription && itemDescription.length > 5) {
                tempTemplate = tempTemplate + '<p><strong>Description: </strong>${Desc}</p>';
                mapOptions.Desc = decodeURIComponent(itemDescription);
            }
            // we need to recreate the infoTemplate otherwise all features will use the 
            // same infoTemplate which will have it's content changed along the way
            infoTemplate = new esri.InfoTemplate('${Name}', tempTemplate);
            mapPoint = new esri.Graphic({'geometry': geometry, 'attributes': mapOptions });
            mapPoint.setInfoTemplate(infoTemplate);
            if(!EEAGeotags.settings.generalIcon) {
                mapPoint.setSymbol(new esri.symbol.PictureMarkerSymbol(icon, 20, 20));
            }
            features.push(mapPoint);
            // set latitude and longitude on each tag as data attribute
            if(locationTagsLen) {
                jQuery(locationTags[i]).data('latitude', item.properties.center[1]);
                jQuery(locationTags[i]).data('longitude', item.properties.center[0]);
            }
        });
        // first is add, second is update, third is delete parameter
        featureLayer.applyEdits(features, null, null);

        EEAGeotags.map.addLayers([featureLayer]);
        EEAGeotags.featureLayer = featureLayer;

        var enableClusterLayer = function() {
            // cluster points 
            var cluster = dojo.map(features, function(item) {
            return { "x": item.geometry.x, "y": item.geometry.y, "attributes": item.attributes, 'template' : item.infoTemplate };
            });

            var clusterLayer = new window.GeotagsClusterLayer({
            "data": cluster,
            "distance": 100,
            "id": "clusters", 
            "labelColor": "#fff",
            "labelOffset": 10,
            "resolution": EEAGeotags.map.extent.getWidth() / EEAGeotags.map.width,
            "singleColor": "#888"
            });
            var defaultSym = new esri.symbol.SimpleMarkerSymbol().setSize(4);
            var renderer = new esri.renderer.ClassBreaksRenderer(
            defaultSym, 
            "clusterCount"
            );
            var greenSymbol = new esri.symbol.PictureMarkerSymbol("http://static.arcgis.com/images/Symbols/Shapes/GreenPin1LargeB.png", 64, 64).setOffset(0, 15);
            var redSymbol = new esri.symbol.PictureMarkerSymbol("http://static.arcgis.com/images/Symbols/Shapes/RedPin1LargeB.png", 72, 72).setOffset(0, 15);
            renderer.addBreak(2, 200, greenSymbol);
            renderer.addBreak(200, 1001, redSymbol);

            clusterLayer.setRenderer(renderer);
            EEAGeotags.map.addLayer(clusterLayer); 
        };
        if (window.GeotagsClusterLayer) {
            enableClusterLayer();
        }

    };

    if(map_points.length) {
        var results = map_points.html();
        results = results.replace(/'/g, "");

        results = jQuery.parseJSON(results);
        setPoints(featureCollection, results);
    }
    else {
        jQuery.getJSON(context_url + '/eea.geotags.jsondata', {}, function (res) {
            setPoints(featureCollection, res.features);
            //center map and display infoWindow when clicking on a geotag
            locationTags.click(function(e) {
                var geometryClick;
                geometryClick = new esri.geometry.Point(jQuery(this).data('latitude'), jQuery(this).data('longitude'));
                geometryClick = esri.geometry.geographicToWebMercator(geometryClick);
                // show infoWindow after clicking on tag name
                var location = jQuery.grep(EEAGeotags.featureLayer.graphics, function(i){return i.geometry.x === geometryClick.x;})[0];
                var point = location.geometry;
                EEAGeotags.map.infoWindow.setFeatures([location]);
                EEAGeotags.map.infoWindow.show(point, self.map.getInfoWindowAnchor(point));
                self.map.infoWindow.resize(250, 150);
                EEAGeotags.map.centerAndZoom(point, 6);
                e.preventDefault();
            });

            if(self.modal === "Events"){
                locationTags.eq(0).trigger('click');
            }
        });
    }
  },

  // Create map
  initMap: function(eea_location_links){
    // To get initial coordonates, zoom to default location and run in debugger: dojo.toJson(map.extent.toJson());
    var self = this;
    var initExtent, basemap;
    initExtent = new esri.geometry.Extent({"xmin": -171, "ymin":-330, "xmax":240, "ymax":140, "spatialReference":{"wkid": 102100}});
    basemap = new esri.layers.ArcGISTiledMapServiceLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer');
    self.map = new esri.Map('eeaEsriMap', {'extent': esri.geometry.geographicToWebMercator(initExtent),
                                           'wrapAround180': true,
                                           'fadeOnZoom': true,
                                           'force3DTransforms': true,
                                           'isScrollWheelZoom': false,
                                           'navigationMode': 'css-transforms'});
    /* self.map.setLevel(10); */
    self.map.addLayer(basemap);
    EEAGeotags.map = self.map;
    // Loading images
    dojo.connect(self.map, 'onUpdateStart', self.showLoading);
    dojo.connect(self.map, 'onUpdateEnd', self.hideLoading);

    dojo.connect(self.map, 'onLoad', function () {
        // Resize the map when the browser resizes
        //
        dojo.ready(function(){
            dojo.connect(dijit.byId('map'), 'resize', self.map, self.map.resize);
            var resize = self.settings.infoWindowSize;
                resize = resize || [140, 100];
            self.map.infoWindow.resize(resize[0], resize[1]);

            // Draw a point on map
            self.drawPoints(eea_location_links);

            // Scalebar
              var scalebar = new esri.dijit.Scalebar({ map: self.map,
                                                      scalebarUnit: 'metric', // Use 'english' for miles
                                                      attachTo: 'bottom-left' });

            // Hack to disable scroll wheel zooming, as map.disableScrollWheelZoom() has no effect
            self.map.onMouseWheel = function () {};
        });
    });
  } 
};

// jQuery plugin for EEAGeotags.View
jQuery.fn.EEAGeotagsView = function(options){
  return this.each(function(){
    var context = jQuery(this).addClass('eea-ajax');
    var geoview = new EEAGeotags.View(context, options);
    context.data('EEAGeotagsView', geoview);
  });
};
