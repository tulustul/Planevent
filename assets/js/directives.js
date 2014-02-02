'use strict';

planevent.directive('addressviewer', function() {
    return {
        restrict: 'EA',
        require: '^ngModel',
        templateUrl: 'assets/partials/directives/addressViewer.html',
        link: function(scope, element, attrs) {
            var map,
                position,
                radiusMarker,
                positionMarker;

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
                    zoom: 5
                };

                var mapElement = $('.address-viewer', element)[0];
                map = new google.maps.Map(mapElement, mapOptions);
            }

            function updatePosition() {
                var address = scope.$eval(attrs.ngModel);
                position = new google.maps.LatLng(52, 19);
                scope.address = address;

                if (positionMarker !== undefined) {
                    positionMarker.setMap(null);
                }

                if (address && address.validated) {
                    position = new google.maps.LatLng(
                            address.latitude, address.longitude);

                    positionMarker = new google.maps.Marker({
                        position: position,
                        map: map,
                        title: address.street + ', ' + address.city
                    });

                    map.setCenter(position);
                    map.setZoom(13);
                }

                updateRadius(false);
            }

            function updateRadius(zoom) {
                var address = scope.$eval(attrs.ngModel),
                    radius = parseInt(scope.$eval(attrs.radius));

                if (zoom === undefined) {
                    zoom = true;
                }

                if (radiusMarker !== undefined) {
                    radiusMarker.setMap(null);
                }

                if (address && address.validated && radius !== undefined) {
                    addRadius(map, position, radius);
                    if (zoom) {
                        map.setZoom(parseInt(140 / (Math.sqrt(radius+2)+9)));
                    }
                }
            }

            initMap();
            scope.$watchCollection(
                '[' + attrs.ngModel + '.longitude,' +
                attrs.ngModel + '.latitude]',
                updatePosition);

            scope.$watch(
                attrs.radius,
                updateRadius
            );
        }
    };
});

planevent.directive('addresssetter', function() {
    return {
        restrict: 'EA',
        require: '^ngModel',
        templateUrl: 'assets/partials/directives/addressSetter.html',
        link: function(scope, element, attrs) {

            scope.validateAddress = function() {
                var address = scope.$eval(attrs.ngModel);
                scope.address = address;

                if (!address.city) {
                    scope.locationComplete = false;
                    return;
                } else {
                    scope.locationComplete = true;
                }
                scope.validatingLocation = true;
                var addressString = address.street + ' ' + address.postal_code +
                                    ' ' + address.city;
                var geocoder = new google.maps.Geocoder();
                geocoder.geocode({'address': addressString},
                    function(results, status) {
                        scope.validatingLocation = false;
                        if (status === google.maps.GeocoderStatus.OK) {
                            var location = results[0].geometry.location;
                            address.latitude = location.d;
                            address.longitude = location.e;
                            address.validated = true;
                        } else {
                            address.latitude = 0;
                            address.longitude = 0;
                            address.validated = false;
                        }
                        scope.$apply();
                    }
                );
            };
        }
    };
});

planevent.directive('gallery', function() {
    return {
        restrict: 'EA',
        require: '^ngModel',
        templateUrl: 'assets/partials/directives/gallery.html',
        link: function($scope, element, attrs) {
            function init() {
                var gallery = $scope.$eval(attrs.ngModel);
                $scope.gallery = gallery;

                $scope._Index = 0;

                $scope.isActive = function (index) {
                    return $scope._Index === index;
                };

                $scope.showPrev = function () {
                    $scope._Index =
                        ($scope._Index > 0) ? --$scope._Index :
                        $scope.gallery.length - 1;
                };

                $scope.showNext = function () {
                    $scope._Index =
                        ($scope._Index < $scope.gallery.length - 1) ?
                        ++$scope._Index : 0;
                };

                $scope.showPhoto = function (index) {
                    $scope._Index = index;
                };
            }

            $scope.$watchCollection('vendor', init);
        }
    };
});
