/* Copyright (C) 2008-2012  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

See the file COPYING for details.
*/

/* Add OpenLayers MapQuest layer management */
OpenLayers.Layer.MapQuestOSM = OpenLayers.Class(OpenLayers.Layer.XYZ, {
    name: "MapQuestOSM",
    sphericalMercator: true,
    url: ' http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.png',
    clone: function(obj) {
        if (obj == null) {
            obj = new OpenLayers.Layer.OSM(
            this.name, this.url, this.getOptions());
        }
        obj = OpenLayers.Layer.XYZ.prototype.clone.apply(this, [obj]);
        return obj;
    },
    CLASS_NAME: "OpenLayers.Layer.MapQuestOSM"
});

/*
* Little hasattr helper
*/
(function ($) {
    $.hasattr = function (key, arr) {
        var v = arr[key];
        if (typeof v === "undefined")
            return false;
        else
            return v; };
})( jQuery );

(function ($) {
    /*
    * Chimere jQuery plugin
    */
        /*
        * Default settings
        */
        var defaults = {
            restricted_extent: false,
            permalink_label: null,
            permalink_div: null,
            permalink: null, // OL Control, could be overrided
            map_layers: null,
            selected_map_layer: null,
            dynamic_categories: false,
            display_submited: false,
            display_feature: null,
            area_id: null,
            checked_categories: [],
            zoom: null,
            lat: null,
            lon: null,
            simple: false,
            // Provide this function to make a custom click event on the marker
            on_marker_click: null,
            // Provide this function to override the feature detail display
            display_feature_detail_fx: null,
            // Provide this function for overriding the getSubcategories default
            get_subcategories_fx: null,
            hide_popup_fx: null,
            controls:[new OpenLayers.Control.Navigation(),
                      new OpenLayers.Control.SimplePanZoom(),
                      new OpenLayers.Control.ScaleLine()],
            maxResolution: 156543.0399,
            units: 'm',
            projection: new OpenLayers.Projection('EPSG:4326'),
            theme:null,
            current_feature: null, // To store the active POI
            current_control: null, // To store the current control
            current_popup: null, // To store the current POI popup displayed
            current_category: null, // To store the current category clicked in list
            icon_offset: new OpenLayers.Pixel(0, 0),
            edition: false, // edition mode
            edition_type_is_route: false, // route or POI edition
            default_icon: new OpenLayers.Icon(
                    'http://www.openlayers.org/dev/img/marker-green.png',
                    new OpenLayers.Size(21, 25),
                    new OpenLayers.Pixel(-(21/2), -25))
        };
        var settings = {};
    /*
    * Publics methods
    */
    var methods = {
        /*
        * Plugin init function
        */
        init: function ( options ) {
            /* Manage parameters */
            settings = $.extend({}, defaults);
            if ( options ) $.extend(settings, options);
            var map_element = $(this).get(0);
            var map_options = {
                controls: settings.controls,
                maxResolution: settings.maxResolution,
                units: settings.units,
                projection: settings.projection,
                theme: settings.theme
            };
            if (settings.restricted_extent){
                settings.restricted_extent.transform(EPSG_DISPLAY_PROJECTION,
                                                     EPSG_PROJECTION);
                map_options['restrictedExtent'] = settings.restricted_extent;
            }

            /* Create map object */
            settings.map = map = new OpenLayers.Map(map_element, map_options);

            /* Manage permalink */
            if (!settings.edition){
                if (settings.permalink == null && !settings.edition) {
                    var permalink_options = {};
                    if (settings.permalink_element){
                        // hard to understand from OL documentation...
                        permalink_options["div"] = settings.permalink_element;
                    }
                    settings.permalink = new OpenLayers.Control.Permalink(
                                                         permalink_options);
                }
                /* HACK new permalink createParams method
                   FIXME when facilities are given to personalize the permalink */
                var oldCreateParams = settings.permalink.createParams
                var  _createParams = function(center, zoom, layers) {
                    // Call normal method
                    var params = oldCreateParams(center, zoom, layers);
                    // Make specific params
                    params.checked_categories = settings.checked_categories;
                    params.display_submited = settings.display_submited;
                    if(settings.current_feature){
                        params.current_feature = settings.current_feature.pk;
                    }
                    return params;
                }
                // Force new createParams method
                settings.permalink.createParams = _createParams;
                settings.map.addControl(settings.permalink);
                // update with the translated permalink label
                if(settings.permalink_label && settings.permalink.div
                   && settings.permalink.div.childNodes.length > 0){
                    settings.permalink.div.childNodes[0].textContent = settings.permalink_label;
                }
            }
            /* Add Layers */
            settings.map.addLayers(settings.map_layers);
            if (settings.map_layers.length > 1){
                settings.map.addControl(new OpenLayers.Control.LayerSwitcher(
                                        {roundedCorner:false}));
            }
            /* select the default map layer */
            if (!settings.selected_map_layer){
                settings.selected_map_layer = 0;
            }
            settings.map.setBaseLayer(
                            settings.map_layers[settings.selected_map_layer]);
            /* Vectors layer */
            settings.layerVectors = new OpenLayers.Layer.Vector("Vector Layer");
            settings.map.addLayer(settings.layerVectors);
            settings.layerVectors.setOpacity(0.8);
            if (settings.edition_type_is_route){
                settings.map.addControl(new OpenLayers.Control.DrawFeature(
                               settings.layerVectors, OpenLayers.Handler.Path));
                settings.map.addControl(new OpenLayers.Control.ModifyFeature(
                        settings.layerVectors, {clickout:false, toggle:false}));
            }
            /* Markers layer */
            settings.layerMarkers = new OpenLayers.Layer.Markers('POIs');
            settings.map.addLayer(settings.layerMarkers);
            settings.layerMarkers.setOpacity(0.8);

            if (settings.dynamic_categories){
                settings.map.events.register('moveend', settings.map,
                                             methods.loadCategories);
            }
            /* TODO make a function */
            if (settings.display_submited) {
                document.getElementById('display_submited_check').checked = true;
            }
            /* if we have some zoom and lon/lat from the init options */
            if (settings.zoom && settings.lon && settings.lat) {
                var centerLonLat = new OpenLayers.LonLat(settings.lon,
                                                         settings.lat);
                centerLonLat.transform(EPSG_DISPLAY_PROJECTION, EPSG_PROJECTION);
                settings.map.setCenter(centerLonLat, settings.zoom);
            }
            /* if not zoom to the extent in cookies */
            else if (!methods.zoomToCurrentExtent(settings.map)){
                /* if no extent in cookies zoom to default */
                if(CENTER_LONLAT && DEFAULT_ZOOM){
                    settings.map.setCenter(CENTER_LONLAT, DEFAULT_ZOOM);
                }
            }

            if (!settings.edition){
                methods.loadCategories();
                methods.loadGeoObjects();
                // Hide popUp when clicking on map
                settings.map.events.register('click', settings.map,
                                             methods.hidePopup);
            } else {
                if (!settings.edition_type_is_route){
                    map.events.register('click', settings.map,
                                        methods.setMarker);
                } else {
                    settings.layerVectors.events.register('featuremodified',
                        settings.layerVectors, helpers.updateRouteForm);
                    settings.layerVectors.events.register('featureadded',
                        settings.layerVectors, helpers.featureRouteCreated);
                }
            }
        }, // end of init

        /*
        * Load markers and route from DB
        */
        loadGeoObjects: function () {
            if($('#waiting').length){$('#waiting').show();}
            helpers.retrieve_checked_categories();
            var ids = settings.checked_categories.join('_');
            if (!ids) ids = '0';
            var uri = extra_url + "getGeoObjects/" + ids;
            if (settings.display_submited) uri += "/A_S";
            $.ajax({url: uri, 
                    dataType: "json",
                    success: function (data) {
                        settings.layerMarkers.clearMarkers();
                        settings.layerVectors.removeAllFeatures();
                        for (var i = 0; i < data.features.length; i++) {
                            var feature = data.features[i];
                            if (feature.geometry.type == 'Point'){
                                methods.addMarker(feature);
                            } else if (feature.geometry.type == 'LineString') {
                                methods.addRoute(feature);
                            }
                        }
                    },
                    error: function (data) {
                        settings.layerMarkers.clearMarkers();
                        settings.layerVectors.removeAllFeatures();
                    },
                    complete: function () {
                        if($('#waiting').length){$('#waiting').hide();}
                    }
                });
        },

        /*
        * Update the categories div in ajax
        */
        loadCategories: function () {
            var current_extent = settings.map.getExtent().transform(
                                            settings.map.getProjectionObject(),
                                            EPSG_DISPLAY_PROJECTION);
            current_extent = current_extent.toArray().join('_')
            current_extent = current_extent.replace(/\./g, 'D');
            current_extent = current_extent.replace(/-/g, 'M');
            var uri = extra_url
            if (settings.area_id) uri += settings.area_id + "/";
            uri += "getAvailableCategories/";
            var params = {"current_extent": current_extent}
            if (settings.display_submited) params["status"] = "A_S";
            $.ajax({url: uri, 
                    data: params, 
                    success: function (data) {
                            $('#categories').html(data);
                            _init_categories();
                            _reCheckCategories();
                            if (settings.current_category) {
                                // TODO : add a force mode 
                                // (in case the category is yet visible in HTML...)
                                methods.toggle_category();
                            }
                        }
                   });
            var _toggle_subcategories = function (category_element) {
                // Check subcategories only if unchecked
                var val = category_element.is(":checked") ? true : false;
                category_element.parent().find("li input").attr("checked", val);
            }
            var _toggle_categories = function (subcategory_element) {
                var parent = subcategory_element.parent().parent().parent();
                var master_check = parent.find("> input");
                if (parent.find('.subcategories input[type=checkbox]').length ==
                    parent.find('.subcategories input[type=checkbox]:checked').length){
                    master_check.attr('checked', 'checked');
                } else {
                    master_check.removeAttr('checked');
                }
                return master_check;
            };
            var _init_categories = function () {
                /*
                * Add event listener in categories DOM elements
                */
                $('#categories #ul_categories > li > input').bind("click", function () {
                    methods.hidePopup();
                    _toggle_subcategories($(this));
                    methods.loadGeoObjects();
                    settings.permalink.updateLink();
                });
                $('.subcategories li input').bind("click", function () {
                    methods.hidePopup();
                    methods.loadGeoObjects();
                    _toggle_categories($(this));
                    settings.permalink.updateLink();
                });
                $('#display_submited_check').bind("click", function () {
                    methods.loadGeoObjects();
                    settings.permalink.updateLink();
                });
                // Zoom to category
                $(".zoom_to_category").bind("click", function (e) {var id = this.id.substr(this.id.lastIndexOf("_")+1); helpers.zoom_to_category(id);});
                $(".zoom_to_subcategory").bind("click", function (e) {var id = this.id.substr(this.id.lastIndexOf("_")+1); helpers.zoom_to_subcategories([id]);});
                $(".toggle_category").bind("click", function (e) {var id = this.id.substr(this.id.lastIndexOf("_")+1); methods.toggle_category(id); });
            }
            var _reCheckCategories = function (){
                /* recheck categories on init or when a redraw occurs */
                if (!settings.checked_categories){
                    return;
                }
                $('#frm_categories .subcategories input:checkbox').each(function(index){
                    cat_id = $(this).attr('id').split('_').pop();
                    if (settings.checked_categories.indexOf(parseInt(cat_id)) != -1) {
                        $(this).attr("checked", "checked");
                        _toggle_categories($(this));
                        methods.toggle_category();
                    } else {
                        $(this).attr("checked", false);
                    }
                });
                if (settings.display_submited == true){
                    $('#display_submited_check').attr("checked", "checked");
                }
            }
        },
        /*
        * Put a marker on the map
        */
        addMarker: function (mark) {
            /*
            * Default Feature configuration
            * This can be overrided in on_marker_click, using settings.current_feature
            */
            var lat = mark.geometry.coordinates[1];
            var lon = mark.geometry.coordinates[0];
            var size = new OpenLayers.Size(mark.properties.icon_width,
                                           mark.properties.icon_height);
            var iconclone = new OpenLayers.Icon(MEDIA_URL + mark.properties.icon_path,
                                            size, settings.icon_offset);
            var feature = new OpenLayers.Feature(settings.layerMarkers,
                      new OpenLayers.LonLat(lon, lat).transform(EPSG_DISPLAY_PROJECTION,
                                                                EPSG_PROJECTION),
                      {icon:iconclone});
            feature.pk = mark.properties.pk;
            feature.popupClass = OpenLayers.Popup.FramedCloud;
            feature.data.popupContentHTML = "<div class='cloud'>";
            feature.data.popupContentHTML += mark.properties.name;
            feature.data.popupContentHTML += "</div>";
            feature.data.overflow = 'hidden';
            var marker = feature.createMarker();
            /* manage markers events */
            var _popup = function() {
                /* show the popup */
                if (settings.current_popup != null) {
                  settings.current_popup.hide();
                }
                if (feature.popup == null) {
                    feature.popup = feature.createPopup();
                    settings.map.addPopup(feature.popup);
                } else {
                    feature.popup.toggle();
                }
                settings.current_popup = feature.popup;
                /* hide on click on the cloud */
                settings.current_popup.groupDiv.onclick = methods.hidePopup;
                settings.permalink.updateLink();
            }
            var markerClick = function (evt) {
                settings.current_feature = feature;
                if ( settings.on_marker_click ) {
                    settings.on_marker_click(evt, mark, settings);
                }
                else
                {
                    // Default popup
                    if (feature.popup && feature.popup.visible()) {
                        if (settings.current_popup == feature.popup) {
                            feature.popup.hide();
                            if (!settings.simple){
                                $('#panel').removeClass('panel-minified');
                                $('#detail').hide();
                            }
                        } else {
                            settings.current_popup.hide();
                            _popup();
                            methods.display_feature_detail(feature.pk);
                        }
                    } else {
                        _popup();
                        methods.display_feature_detail(feature.pk);
                    }
                }
                OpenLayers.Event.stop(evt);
            };
            var markerOver = function (evt) {
                document.body.style.cursor='pointer';
                OpenLayers.Event.stop(evt);
            };
            var markerOut = function (evt) {
                document.body.style.cursor='auto';
                OpenLayers.Event.stop(evt);
            };
            marker.events.register('click', feature, markerClick);
            marker.events.register('mouseover', feature, markerOver);
            marker.events.register('mouseout', feature, markerOut);
            settings.layerMarkers.addMarker(marker);
            /* show the item when designed in the permalink */
            if (settings.display_feature == feature.pk){
                _popup(feature);
                methods.display_feature_detail(feature.pk);
                settings.map.setCenter(feature.lonlat, 16);
                methods.loadCategories();
            }
            return feature;
        },

        /*
        * Put a route on the map
        */
        addRoute: function(route) {
            var polyline = route.geometry;
            var point_array = new Array();
            for (i=0; i<polyline.coordinates.length; i++){
                var point = new OpenLayers.Geometry.Point(polyline.coordinates[i][0],
                                                          polyline.coordinates[i][1]);
                point_array.push(point);
            }
            var linestring = new OpenLayers.Geometry.LineString(point_array);
            linestring.transform(EPSG_DISPLAY_PROJECTION, settings.map.getProjectionObject());
            settings.current_feature = new OpenLayers.Feature.Vector();

            var style = OpenLayers.Util.extend({},
                                        OpenLayers.Feature.Vector.style['default']);
            style.strokeColor = route.properties.color;
            style.strokeWidth = 3;
            settings.current_feature.style = style;
            settings.current_feature.geometry = linestring;
            settings.layerVectors.addFeatures([settings.current_feature]);
        },
        display_feature_detail: function (pk) {
            /*
            * update current detail panel with an AJAX request
            */
            var uri = extra_url
            if (settings.area_id) uri += settings.area_id + "/"
            uri += "getDetail/" + pk;
            var params = {}
            if (settings.simple) { params["simple"] = 1; }
            $.ajax({url: uri, 
                    data: params, 
                    success: function (data) {
                            if ( settings.display_feature_detail_fx ) {
                                // Custom function ?
                                settings.display_feature_detail_fx(data, settings);
                            }
                            else {
                                if (!settings.simple) {
                                    $('#panel').addClass('panel-minified');
                                    $('#detail').html(data).show();
                                }
                                else {
                                    settings.current_popup.setContentHTML("<div class='cloud'>" + data + "</div>");
                                }
                            }
                        }
                   });
        },
        center_on_feature: function(feature) {
            var f = get_or_set(feature, settings.current_feature);
            if (f)
            {
                settings.map.setCenter(f.lonlat);
            }
        },
        zoom: function (options) {
            if ($.hasattr("category", options)) {
                helpers.zoom_to_category(options["category"]);
            } else if ($.hasattr("subcategories", options)) {
                helpers.zoom_to_subcategories(options["subcategories"]);
            } else if ($.hasattr("area", options)) {
                helpers.zoom_to_area(options["area"]);
            }
        },
        category_detail: function (category_id) {
            /* show the detail of a category */
            var uri = extra_url + "getDescriptionDetail/" + category_id;
            $.ajax({url:uri,
                        success: function (data) {
                            $("#category_detail").html(data).dialog();
                            $("#category_detail").dialog( "option", "title",
                                    $("#category_title").html());
                        }
                  });
        },
        toggle_category: function (id) {
            // TODO make this id DOM element customisable
            // Check if element is currently visible or not
            var was_visible = $("#maincategory_" + id).is(":visible");
            // Close all categories
            $("#categories ul.subcategories").hide();
            // Put a minus image
            $("#categories img.toggle_category").attr("src", STATIC_URL + "chimere/img/plus.png");
            if (!was_visible)
            {
                // Show the subcategories
                $("#maincategory_" + id).toggle();
                // Put a plus image
                $("#maincategory_img_" + id).attr("src", STATIC_URL + "chimere/img/minus.png");
                settings.current_category = id;
            }
        },
        zoomToCurrentExtent: function(){
            /* zoom to current extent */
            var current_extent = helpers.getSavedExtent();
            var extent;
            if (OpenLayers && current_extent && current_extent.length == 4){
                extent = new OpenLayers.Bounds(
                                current_extent[0], current_extent[1],
                                current_extent[2], current_extent[3]);
            }
            /*
            else if (OpenLayers && default_area && default_area.length == 4){
                extent = new OpenLayers.Bounds(default_area[0], default_area[1],
                                               default_area[2], default_area[3]);
            }*/
            else{
                return;
            }
            extent.transform(EPSG_DISPLAY_PROJECTION, EPSG_PROJECTION);
            settings.map.zoomToExtent(extent, true);
            return true;
        },
        // methods for edition
        setMarker: function (event){
            event = event || window.event;
            var lonlat = settings.map.getLonLatFromViewPortPx(event.xy);
            methods.putEditMarker(lonlat, false);
            OpenLayers.Event.stop(event);
        },
        /* put the marker on the map and update latitude and longitude fields */
        putEditMarker: function (lonlat, zoom){
            if (settings.current_feature) {
                settings.layerMarkers.removeMarker(settings.current_feature);
            }
            settings.current_feature = new OpenLayers.Marker(lonlat.clone(),
                                                      settings.default_icon);
            settings.layerMarkers.addMarker(settings.current_feature);
            lonlat = lonlat.clone().transform(settings.map.getProjectionObject(),
                                              EPSG_DISPLAY_PROJECTION);
            $('#id_point').val('POINT(' + lonlat.lon + ' ' + lonlat.lat + ')');
            $('#live_latitude').val(lonlat.lat);
            $('#live_longitude').val(lonlat.lon);
            /* zoom to the point */
            if (zoom){
                var bounds = settings.layerMarkers.getDataExtent();
                if (bounds) settings.map.zoomToExtent(bounds);
            }
            return;
        },
        activateCurrentControl: function(){
            if (settings.current_control){
                settings.current_control.activate();
            } else {
                var pathCreate = settings.map.getControlsByClass(
                                        'OpenLayers.Control.DrawFeature');
                if (pathCreate){
                    pathCreate[0].activate();
                }
            }
            var pathModify = settings.map.getControlsByClass(
                                      'OpenLayers.Control.ModifyFeature');
            if (settings.current_feature && pathModify){
                pathModify[0].selectControl.select(settings.current_feature);
            }
        },
        deactivateCurrentControl: function(){
            if (settings.current_control){
                settings.current_control.deactivate();
            }
        },
        initFeature: function(json_geometry){
            var json = new OpenLayers.Format.JSON();
            var polyline = json.read(json_geometry);
            var point_array = new Array();
            for (i=0; i<polyline.coordinates.length; i++){
                var point = new OpenLayers.Geometry.Point(
                                    polyline.coordinates[i][0],
                                    polyline.coordinates[i][1]);
                point_array.push(point);
            }
            var linestring = new OpenLayers.Geometry.LineString(point_array);
            methods.initFeatureFromGeometry(linestring);
        },
        initFeatureFromWkt: function(wkt_geometry){
            var linestring = OpenLayers.Geometry.fromWKT(wkt_geometry);
            methods.initFeatureFromGeometry(linestring);
        },
        initFeatureFromGeometry: function(linestring){
            linestring.transform(EPSG_DISPLAY_PROJECTION,
                                 EPSG_PROJECTION);
            currentFeature = new OpenLayers.Feature.Vector();
            currentFeature.geometry = linestring;
            settings.layerVectors.removeFeatures();
            settings.layerVectors.addFeatures([currentFeature]);
            var pathModify = settings.map.getControlsByClass(
                                        'OpenLayers.Control.ModifyFeature');
            if (pathModify){
                settings.current_control = pathModify[0];
            }
            /*zoom to the route*/
            var bounds = settings.layerVectors.getDataExtent();
            if (bounds) settings.map.zoomToExtent(bounds);
        },
        hidePopup: function (evt) {
            if (settings.hide_popup_fx) {
                settings.hide_popup_fx(evt, settings)
            }
            else { // Default behaviour
                if (settings.current_popup)
                {
                    settings.current_popup.hide();
                    if (!settings.simple){
                        $('#panel').removeClass('panel-minified');
                        $('#detail').hide();
                    }
                }
            }
        },
        saveExtent: function(){
            var extent_key = 'MAP_EXTENT';
            //if (area_name){ extent_key = extent_key + '_' + area_name; }
            if (!settings.map) return;
            var extent = settings.map.getExtent().transform(EPSG_PROJECTION,
                                                   EPSG_DISPLAY_PROJECTION);
            document.cookie = extent_key + '=' + extent.toArray().join('_')
                              + ';path=/';
        }
    }; // End of public methods
    var helpers = {
        getSubcategories: function (category_id) {
            if(settings.get_subcategories_fx) {
                return settings.get_subcategories_fx(category_id, settings);
            }
            else {
                var ul = document.getElementById('maincategory_'+category_id);
                var subcats = new Array();
                for (i in ul.children){
                    var li = ul.children[i];
                    if (li.id){
                        subcats.push(li.id.split('_').pop());
                    }
                }
                return subcats;
            }
        },
        retrieve_checked_categories: function () {
            /*
            * Retrieve checked_categories, and store it in settings 
            */
            var initialized = false;
            $('#frm_categories .subcategories input:checkbox').each(
                function(index){
                    if (!initialized){
                        initialized = true;
                        settings.checked_categories = [];
                        settings.display_submited = false;
                    }
                    if ($(this).attr('checked') == 'checked' || $(this).attr('checked') == true){
                        cat_id = $(this).attr('id').split('_').pop();
                        settings.checked_categories.push(parseInt(cat_id));
                    }
            });
            if(initialized && ($('#display_submited_check').attr("checked") == "checked" || $('#display_submited_check').attr("checked") == true)){
                settings.display_submited = true;
            }
        },
        zoom_to: function (bounds) {
            settings.map.zoomToExtent(bounds)
        },
        zoom_to_subcategories: function (ids) {
            // TODO add markers and check the subcategory, if not yet checked/displayed
            var ids = ids.join('_');
            if (!ids) ids = '0';
            var uri = extra_url + "getGeoObjects/" + ids;
            if (settings.display_submited) uri += "/A_S";
            $.ajax({url: uri, 
                    dataType: "json",
                    success: function (data) {
                        // Create a generic bounds
                        var lon, lat, feature;
                        var bounds = new OpenLayers.Bounds()
                        for (var i = 0; i < data.features.length; i++) {
                            feature = data.features[i];
                            if (feature.geometry.type == 'Point') {
                                    lat = feature.geometry.coordinates[1];
                                    lon = feature.geometry.coordinates[0];
                                    bounds.extend(new OpenLayers.LonLat(lon, lat).transform(EPSG_DISPLAY_PROJECTION, EPSG_PROJECTION));
                            } else if (feature.geometry.type == 'LineString') {
                                // TODO
                            }
                        }
                        helpers.zoom_to(bounds);
                   }
               });
        },
        zoom_to_category: function (id) {
            helpers.zoom_to_subcategories(helpers.getSubcategories(id));
        },
        zoom_to_area: function (coords) {
            /* zoom to an area */
            var left = coords[0];
            var bottom = coords[1];
            var right = coords[2];
            var top = coords[3];
            var bounds = new OpenLayers.Bounds(left, bottom, right, top);
            bounds.transform(EPSG_DISPLAY_PROJECTION, EPSG_PROJECTION);
            settings.map.zoomToExtent(bounds, true);
            if (settings.dynamic_categories) {
                methods.loadCategories();
            }
        },
        getSavedExtent: function() {
            /* get the current extent from a cookie */
            var cookies = document.cookie.split(';');
            var map_extent;
            var extent_key = 'MAP_EXTENT';
            //if (area_name){ extent_key = extent_key + '_' + area_name; }
            for (var i=0; i < cookies.length; i++){
                var items = cookies[i].split('=');
                key = items[0].split(' ').join('');
                if (key == extent_key && !map_extent){
                    map_extent = items[1].split('_');
                }
            }
            return map_extent;
        },
        featureRouteCreated: function(event) {
            /* toggle to edition mode */
            var pathModify = settings.map.getControlsByClass(
                                         'OpenLayers.Control.ModifyFeature')[0];
            var pathCreate = settings.map.getControlsByClass(
                                         'OpenLayers.Control.DrawFeature')[0];
            pathCreate.deactivate();
            settings.current_control = pathModify;
            jQuery('#help-route-create').hide();
            jQuery('#help-route-modify').show();
            pathModify.activate();
            helpers.updateRouteForm(event);
            pathModify.selectControl.select(event.feature);
        },
        updateRouteForm: function(event) {
            /* update the form */
            if (event){
                settings.current_feature = event.feature;
            }
            var current_geo = settings.current_feature.geometry.clone();
            current_geo.transform(EPSG_PROJECTION, EPSG_DISPLAY_PROJECTION);
            jQuery('#id_route').val(current_geo);
            var vertices = current_geo.getVertices();
            if (vertices){
                jQuery('#id_point').val(vertices);
            }
        }

    }; // End of helpers

    $.fn.chimere = function (thing) {
        // Method calling logic
        if ( methods[thing] ) {
            return methods[ thing ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        }
        else if ( typeof thing === 'object' || ! thing ) {
            return methods.init.apply( this, arguments );
        }
        else if ( thing === 'settings' ) {
            // Use $("#mydiv").chimere("settings", "key", "value") to change settings
            // from outside the plugin
            if (arguments.length == 3) {
                settings[arguments[1]] = arguments[2];
            }
            else if (arguments.length == 2) {
                return settings[arguments[1]];
            }
            else { // Use $("#mydiv").chimere("settings") to know the current settings
                return settings;
            }
        }
        else {
            $.error( 'Method ' +  thing + ' does not exist on jQuery.chimere' );
        }
            
        return this;
    };
})( jQuery );
