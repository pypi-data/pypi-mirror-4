(function($) {
$.fn.m01GMapWidget = function (settings) {
    settings = $.extend({
        address: null,
        centerAfterInfoClose: true,
        iconAnchorXOffset: 0,
        iconAnchorYOffset: 0,
        iconHeight: null,
        iconShadowURL: null,
        iconURL: null,
        iconWidth: null,
        infoWindowAnchorXOffset: 0,
        infoWindowAnchorYOffset: 0,
        infoWindowContent: null,
        latitude: null,
        latitudeExpression: null,
        longitude: null,
        longitudeExpression: null,
        mapType: G_NORMAL_MAP,
        mode: 'display',
        removeMarkerOnDBClick: true,
        zoom: 11
    }, settings);

    // set initial vars
    var map = false;
    var marker = false;
    var geocoder = false;
    var isInput = false;
    if (settings.mode == 'input') {
        isInput = true;
    }

    function setLatLong(latitude, longitude) {
        $(settings.latitudeExpression).val(latitude);
        $(settings.longitudeExpression).val(longitude);
    }

    function showInfo() {
        if (settings.infoWindowContent) {
            marker.openInfoWindowHtml(settings.infoWindowContent);
        }
    }

    function getGIcon() {
        var icon = null;
        if (settings.iconURL) {
            var icon = new GIcon();
            icon.image = settings.iconURL;
            if (settings.iconShadowURL) {
                icon.shadow = settings.iconShadowURL;
            }
            icon.iconSize = new GSize(settings.iconWidth, settings.iconHeight);
            icon.iconAnchor = new GPoint(settings.iconAnchorXOffset,
                settings.iconAnchorYOffset);
            icon.infoWindowAnchor = new GPoint(settings.infoWindowAnchorXOffset,
                settings.infoWindowAnchorYOffset);
        }
        return icon;
    }

    function applyHandler() {
        if (settings.removeMarkerOnDBClick && isInput) {
            GEvent.addListener(marker, 'dblclick', function() {
                // reset lat, lng and remove marker
                setLatLong('', '');
                map.removeOverlay(marker);
            });
        }
        GEvent.addListener(marker, "click", function() {
            showInfo();
        });
        if (settings.centerAfterInfoClose) {
            GEvent.addListener(marker, "infowindowclose", function() {
                mPoint = marker.getPoint();
                lat = mPoint.lat();
                lng = mPoint.lng();
                map.setCenter(new GLatLng(lat, lng));
            });
        }
        if (isInput) {
            GEvent.addListener(marker, "dragstart", function() {
                map.closeInfoWindow();
            });
            GEvent.addListener(marker, "dragend", function() {
                newPoint = marker.getPoint();
                var lat = newPoint.lat();
                var lng = newPoint.lng();
                setLatLong(lat, lng);
                map.setCenter(new GLatLng(lat, lng));
                showInfo(marker);
            });
        }
    }

    function setupMarkerPoint(point, zoom) {
        map.setCenter(point, zoom, settings.mapType);
        icon = getGIcon();
        marker = new GMarker(point, {icon: icon, draggable: isInput});
        applyHandler();
        setLatLong(point.lat(), point.lng());
        map.addOverlay(marker);
        map.setCenter(point);
    }

    function setupMarkerPointCallback(point) {
        if (point) {
            map.setCenter(point, settings.zoom, settings.mapType);
            icon = getGIcon();
            marker = new GMarker(point, {icon: icon, draggable: isInput});
            applyHandler();
            map.addOverlay(marker);
            setLatLong(point.lat(), point.lng());
        } else {
            map.setCenter(new GLatLng(10, 10));
            var myEventListener = GEvent.bind(map, "click", this, function(overlay, latlng) {
                if (!marker) {
                    if (latlng) {
                        setupMarkerPoint(latlng, map.getZoom());
                    } else if(overlay instanceof GMarker) {
                        map.removeOverlay(marker);
                    }
                } else {
                    GEvent.removeListener(myEventListener);
                }
            }); 
        }
    }

    function setupMarker() {
        if (settings.latitude && settings.longitude) {
            var aPoint = new GLatLng(settings.latitude, settings.longitude);
            setupMarkerPoint(aPoint, settings.zoom);
        }else if (settings.address){
            geocoder = new GClientGeocoder();
            geocoder.getLatLng(settings.address, setupMarkerPointCallback);
        }else {
            alert("No initial address or latitude/longitude is given"); //p01.checker.silence
        }
    }

    // render the GMap
    function renderGMap(self) {
        if (GBrowserIsCompatible()) {
            map = new GMap2(self);
            map.enableDoubleClickZoom();
            map.enableContinuousZoom();
            map.addControl(new GSmallMapControl());
            map.addControl(new GMapTypeControl());
            setupMarker();
        }
    }

    // render google maps
    return $(this).each(function(){
        renderGMap(this);
        // prevent from memory leak
        $(window).unload(function () {
            GUnload();
            marker = false;
            map = false;
            geocoder = false;
        });
    });
};
})(jQuery);
