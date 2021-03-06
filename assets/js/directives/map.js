'use strict';

angular.module('planevent').directive('addressviewer', function($timeout) {
    return {
        restrict: 'EA',
        require: '^ngModel',
        templateUrl: 'assets/partials/directives/addressViewer.html',
        link: function(scope, element, attrs) {
            var map,
            position,
            radiusMarker,
            positionMarker,
            cluster,
            searchMarkers = [];

            function addRadius(map, center, radius) {
                var circleOptions = {
                    strokeColor: '#AA5500',
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: '#99FF33',
                    fillOpacity: 0.2,
                    map: map,
                    center: center,
                    radius: radius*1000
                };
                radiusMarker = new google.maps.Circle(circleOptions);
            }

            function initMap() {
                var mapOptions = {
                    center: new google.maps.LatLng(52, 19),
                    zoom: 5,
                    scrollwheel: false,
                };

                var mapElement = $('.address-viewer .map', element)[0];
                map = new google.maps.Map(mapElement, mapOptions);
            }

            function updatePosition() {
                var address = scope.$eval(attrs.ngModel),
                scaleRadiusOnly = attrs.scalePolicy === 'radius-only';
                position = new google.maps.LatLng(52, 19);
                scope.address = address;

                if (positionMarker !== undefined) {
                    positionMarker.setMap(null);
                }

                if (address && address.validated) {
                    position = new google.maps.LatLng(
                        address.latitude, address.longitude
                    );

                    positionMarker = new google.maps.Marker({
                        position: position,
                        map: map,
                        title: address.formatted
                    });

                    map.setCenter(position);
                    if (!scaleRadiusOnly) {
                        map.setZoom(13);
                    }
                }

                updateRadius(scaleRadiusOnly);
            }

            function updateRadius(zoom) {
                var address = scope.$eval(attrs.ngModel),
                radius = scope.$eval(attrs.radius);

                if (radius === undefined) {
                    return;
                }
                radius = parseInt(radius);

                if (zoom === undefined) {
                    zoom = true;
                }

                if (radiusMarker !== undefined) {
                    radiusMarker.setMap(null);
                }

                if (address && address.validated && radius !== undefined) {
                    addRadius(map, position, radius);
                    if (zoom) {
                        map.setCenter(position);
                        map.setZoom(parseInt(140 / (Math.sqrt(radius+2)+9)));
                    }
                }
            }

            function updateMarkers() {
                var offer, position, i;

                for (i = 0; i < searchMarkers.length; i++ ) {
                    searchMarkers[i].setMap(null);
                }
                searchMarkers.length = 0;

                for (i in scope.entities) {
                    offer =  scope.entities[i];
                    position = new google.maps.LatLng(
                        offer.address.latitude,
                        offer.address.longitude
                    );
                    searchMarkers.push(new google.maps.Marker({
                        position: position,
                        title: offer.name + ' ' + offer.address.formatted
                    }));
                }

                if (cluster !== undefined) {
                    cluster.clearMarkers();
                } else {
                    cluster = new MarkerClusterer(map);
                }

                cluster.addMarkers(searchMarkers);
            }

            function clearMarkers() {
                cluster.clearMarkers();
            }

            function updateMap(time) {
                var center = map.getCenter();
                $timeout(function() {
                    google.maps.event.trigger(map, 'resize');
                    map.setCenter(center);
                }, time*1000);
            }

            if ('updateFunctionName' in attrs) {
                scope[attrs.updateFunctionName] = updateMap;
            }

            if ('clearMarkersFunctionName' in attrs) {
                scope[attrs.clearMarkersFunctionName] = clearMarkers;
            }

            initMap();
            scope.$watchCollection(
                                   '[' + attrs.ngModel + '.longitude,' +
                                   attrs.ngModel + '.latitude]',
                                   updatePosition);

            if (attrs.radius !== undefined) {
                scope.$watch(attrs.radius, updateRadius);
            }
            scope.$watch('entities', updateMarkers);

            var viewerElement = $('.address-viewer .map', element);
            scope.$watch(
                function() {
                    return viewerElement.is(':visible');
                },
                function() {
                    var center = map.getCenter();
                    google.maps.event.trigger(map, 'resize');
                    map.setCenter(center);
                }
            );
        }
    };
});

angular.module('planevent').directive('addresssetter', function() {
    return {
        restrict: 'EA',
        require: '^ngModel',
        templateUrl: 'assets/partials/directives/addressSetter.html',
        link: function(scope, element, attrs, ngModel) {
            scope.locationLabel = attrs.label;

            function parseResponse(result) {
                if (result === undefined) {
                    return;
                }

                var type, component,
                    street = ' ',
                    location = result.geometry.location,
                    address_components = result.address_components,
                    address = ngModel.$viewValue;

                address.formatted = result.formatted_address;

                for (var i = address_components.length - 1; i >= 0; i--) {
                    type = address_components[i].types[0];
                    component = address_components[i].long_name;

                    if (type === 'street_number') {
                        street += component;
                    } else if (type === 'route') {
                        street = component + street;
                    } else if (type === 'administrative_area_level_3') {
                        address.city = component;
                    }
                }

                if (street !== ' ') {
                    address.street = street;
                }

                address.latitude = location.k;
                address.longitude = location.B;

                address.validated = true;
            }

            scope.validateAddress = function() {
                scope.validatingLocation = true;
                var geocoder = new google.maps.Geocoder();
                geocoder.geocode(
                    {'address': scope.addressString},
                    geocodeCallback
                );
            };

            function geocodeCallback(results, status) {
                var address = ngModel.$viewValue;

                scope.validatingLocation = false;
                if (status === google.maps.GeocoderStatus.OK) {
                    parseResponse(results[0]);
                    address.validated = true;
                } else {
                    address.validated = false;
                }
            }

            scope.$watch('details', function() {
                parseResponse(scope.details);
            });
        }
    };
});
