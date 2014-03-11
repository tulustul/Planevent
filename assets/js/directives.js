'use strict';

angular.module('planevent').directive('addressviewer', function() {
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
                var address = scope.$eval(attrs.ngModel),
                scaleRadiusOnly = attrs.scalePolicy === 'radius-only';
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

            initMap();
            scope.$watchCollection(
                                   '[' + attrs.ngModel + '.longitude,' +
                                   attrs.ngModel + '.latitude]',
                                   updatePosition);

            scope.$watch(
                         attrs.radius,
                         updateRadius
                         );

            scope.$watch(
                         attrs.radius,
                         updateRadius
                         );

            var viewerElement = $('.address-viewer', element);
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
        link: function(scope, element, attrs) {
            var address;

            scope.locationLabel = attrs.label;
            scope.type = attrs.type;

            function parseResponse(result) {
                var type, component,
                street = ' ',
                location = result.geometry.location,
                address_components = result.address_components;

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

                address.latitude = location.d;
                address.longitude = location.e;
            }

            function processMultilineAddress() {
                if (!address.city) {
                    scope.locationComplete = false;
                    return;
                } else {
                    scope.locationComplete = true;
                }
                scope.addressString = '';
                if (address.street !== undefined) {
                    scope.addressString += address.street + ' ';
                }
                if (address.city !== undefined) {
                    scope.addressString += address.city;
                }
            }

            scope.validateAddress = function() {
                address = scope.$eval(attrs.ngModel);

                if (scope.type !== 'simple') {
                    processMultilineAddress();
                }

                scope.validatingLocation = true;
                var geocoder = new google.maps.Geocoder();
                geocoder.geocode(
                                 {'address': scope.addressString},
                                 geocodeCallback
                                 );
            };

            function geocodeCallback(results, status) {
                scope.validatingLocation = false;
                if (status === google.maps.GeocoderStatus.OK) {
                    parseResponse(results[0]);
                    address.validated = true;
                } else {
                    address.validated = false;
                }
                scope.$apply();
            }
        }
    };
});

angular.module('planevent').directive('gallery', function() {
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

angular.module('planevent').directive('experiment',
        function($http) {
    return {
        restrict: 'EA',
        require: '^experiment',
        controller: 'ExperimentController',
        transclude: true,
        templateUrl: 'assets/partials/directives/experiment.html',

        compile: function() {
            return function(scope, element, attrs) {
                var experiment = attrs.id,
                storageKey = 'planevent:experiment:' + experiment,
                variation = localStorage.getItem(storageKey);
                if (variation === null) {
                    var url = '/api/experiment/' + attrs.id + '/variation';
                    $http.get(url).success(function(variation) {
                        localStorage.setItem(storageKey, variation);
                        scope.setVariation(element, experiment, variation);
                    });
                } else {
                    scope.setVariation(element, experiment, variation);
                }
            };
        }
    };
});

angular.module('planevent').directive('pebutton', function() {
    return {
        restrict: 'EA',
        scope: {
            'watch': '&watch',
        },
        templateUrl: 'assets/partials/directives/button.html',

        link: function(scope, element, attrs) {

            function updateHref() {
                if ('href' in attrs) {
                    $('a', element).attr('href', attrs.href);
                }
            }

            scope.class_ = '';

            if ('buttonSlide' in attrs) {
                scope.class_ += '-slide';
            }

            if ('textPosition' in attrs) {
                scope.class_ += '-' + attrs.textPosition;
            }

            scope.icon = attrs.icon;
            scope.text = attrs.text;

            updateHref();

            if ('watch' in attrs) {
                scope.$watch(scope.watch, updateHref);
            }
        }
    };
});

/* Basing on ng-infinite-scroll - v1.0.0 */
angular.module('planevent').directive('infinitescroll',
        function($window, $rootScope, $timeout, searchService) {
    return {
        restrict: 'EA',
        scope: '=',
        transclude: true,
        templateUrl: 'assets/partials/directives/infiniteScroll.html',

        link: function(scope, elem, attrs) {
            // searchService.count(function(count) {
            //     scope.count = count;
            // });

            var checkWhenEnabled, handler, scrollDistance, scrollEnabled;
            $window = angular.element($window);
            scrollDistance = 0;
            if (attrs.distance !== null) {
                scope.$watch(attrs.distance, function(value) {
                    return scrollDistance = parseInt(value, 10);
                });
            }
            scrollEnabled = true;
            checkWhenEnabled = false;
            if (attrs.infiniteScrollDisabled !== null) {
                scope.$watch(attrs.infiniteScrollDisabled, function(value) {
                    scrollEnabled = !value;
                    if (scrollEnabled && checkWhenEnabled) {
                        checkWhenEnabled = false;
                        return handler();
                    }
                });
            }
            handler = function() {
                var elementBottom, remaining, shouldScroll, windowBottom;
                windowBottom = window.innerHeight + $window.scrollTop();
                elementBottom = elem.offset().top + elem.height();
                remaining = elementBottom - windowBottom;
                shouldScroll = remaining <= window.innerHeight * scrollDistance;
                if (shouldScroll && scrollEnabled) {
                    if ($rootScope.$$phase) {
                        return scope.$eval(attrs.fetchFunction);
                    } else {
                        return scope.$apply(attrs.fetchFunction);
                    }
                } else if (shouldScroll) {
                    return checkWhenEnabled = true;
                }
            };
            $window.on('scroll', handler);
            scope.$on('$destroy', function() {
                return $window.off('scroll', handler);
            });
            return $timeout((function() {
                if (attrs.infiniteScrollImmediateCheck) {
                    if (scope.$eval(attrs.infiniteScrollImmediateCheck)) {
                        return handler();
                    }
                } else {
                    return handler();
                }
            }), 0);
        }
    };
});

angular.module('planevent').directive('vendorpreview', function() {
    return {
        restrict: 'EA',
        scope: {
            'vendor': '=vendor',
        },
        templateUrl: 'assets/partials/directives/vendorPreview.html',
    };
});
