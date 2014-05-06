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

            scope.$watch(attrs.radius, updateRadius);
            scope.$watch('entities', updateMarkers);

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
            var address = scope.$eval(attrs.ngModel);

            scope.locationLabel = attrs.label;
            scope.type = attrs.type;

            function parseResponse(result) {
                if (result === undefined) {
                    return;
                }

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

                address.latitude = location.k;
                address.longitude = location.A;

                address.validated = true;

                scope[attrs.ngModel] = address;
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

            scope.$watch('details', function() {
                parseResponse(scope.details);
            });
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

            $scope.$watchCollection('offer', init);
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
        transclude: true,

        link: function(scope, element, attrs) {

            function updateHref() {
                if ('href' in attrs) {
                    $('a', element).attr('href', attrs.href);
                }
            }

            function updateText() {
                scope.text = scope.$eval(attrs.textModel);
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

            if ('textModel' in attrs) {
                scope.$watch('loggedUser', updateText);
            }
        }
    };
});

/* Basing on ng-infinite-scroll - v1.0.0 */
angular.module('planevent').directive('infinitescroll',
        function($window, $rootScope, $timeout, $location, $routeParams) {

    $window = angular.element($window);

    return {
        restrict: 'EA',
        scope: '=',
        transclude: true,
        templateUrl: 'assets/partials/directives/infiniteScroll.html',

        link: function(scope, elem, attrs) {
            var autoScroolLimit = parseInt(attrs.autoScrollLimit),
                fetchFunction = scope.$eval(attrs.fetchFunction),
                offset = parseInt($routeParams.offset),
                loadingPrevious = false,
                checkWhenEnabled, scrollDistance, scrollEnabled,
                minLoadedOffset, maxLoadedOffset, pageSize;

            calculatePageSize(attrs.elementSize);

            if (isNaN(offset)) {
                offset = 0;
            }
            minLoadedOffset = offset;
            maxLoadedOffset = offset;

            scope.entities = [];
            scope.pages = [];
            scope.topIsLoaded = true;
            scope.bottomIsLoaded = false;
            scope.manualNextLoading = false;
            scope.waitingForMore = false;
            scope.minLoadedOffset = minLoadedOffset;
            scope.maxLoadedOffset = maxLoadedOffset;
            scope.currentPage = 0;

            prepareScrolling();

            scope.fetchPage = function(page) {
                if (page >= minLoadedOffset && page <= maxLoadedOffset) {
                    scrollToPage(page);

                } else if (page >= minLoadedOffset - 2*pageSize &&
                           page < minLoadedOffset) {
                    fetchEntities(page, minLoadedOffset - page,
                                  function(entities) {
                        scope.entities = _.union(entities, scope.entities);
                        minLoadedOffset = page;
                        return 0;
                    });

                } else if (page <= maxLoadedOffset + 2*pageSize &&
                           page > maxLoadedOffset) {
                    fetchEntities(maxLoadedOffset, page - maxLoadedOffset,
                                  function(entities) {
                        scope.entities = _.union(scope.entities, entities);
                        maxLoadedOffset += entities.length;
                        return page;
                    });

                } else {
                    minLoadedOffset = page;
                    fetchEntities(minLoadedOffset, pageSize,
                                  function(entities) {
                        scope.entities = entities;
                        maxLoadedOffset = minLoadedOffset + entities.length;
                        return 0;
                    });
                }
            };
            scope.loadPrevious = function() {
                var newMinLoadedOffset = _.max([0, minLoadedOffset - pageSize]);
                var limit = minLoadedOffset - newMinLoadedOffset;
                minLoadedOffset = newMinLoadedOffset;
                loadingPrevious = true;
                fetchEntities(minLoadedOffset, limit, function(entities) {
                    scope.entities = _.union(entities, scope.entities);
                    loadingPrevious = false;
                    return 0;
                });
            };
            scope.loadNext = function() {
                fetchEntities(maxLoadedOffset, pageSize, function(entities) {
                    scope.entities = _.union(scope.entities, entities);
                    maxLoadedOffset += entities.length;
                });
            };

            function reset(resetOffset) {
                scope.entities = [];
                if (resetOffset === false) {
                    minLoadedOffset = offset;
                } else {
                    minLoadedOffset = 0;
                }
                maxLoadedOffset = 0;
                fetchEntities(0, pageSize, function(entities) {
                    scope.entities = entities;
                    maxLoadedOffset += entities.length;
                    return 0;
                });
            }
            scope[attrs.resetFunctionName] = reset;

            function calculatePageSize() {
                var elementSize = scope.$eval(attrs.elementSize),
                    containerWidth = $('.infinite-scroll > .content').width(),
                    viewportHeight = $(window).height(),
                    fetchPages = parseInt(attrs.fetchPages);

                pageSize = parseInt(containerWidth / elementSize.width) *
                    parseInt((viewportHeight * fetchPages) /
                             elementSize.height);
            }

            $(window).resize(function() {
                calculatePageSize();
                handler();
            });

            function generatePages() {
                scope.pages = _.range(0, scope.totalCount, pageSize);
            }

            function fetchEntities(offset, limit, callback) {
                if (loadingPrevious) {
                    scope.waitingForMore = 'top';
                } else {
                    scope.waitingForMore = 'bottom';
                }
                fetchFunction(offset, limit,
                        function(totalCount, entities) {
                    scope.totalCount = totalCount;
                    var page = callback(entities);
                    scope.topIsLoaded = minLoadedOffset === 0;
                    scope.bottomIsLoaded = maxLoadedOffset === scope.totalCount;
                    scope.manualNextLoading =
                        (maxLoadedOffset - minLoadedOffset) > autoScroolLimit;
                    scope.waitingForMore = false;
                    scope.minLoadedOffset = minLoadedOffset;
                    scope.maxLoadedOffset = maxLoadedOffset;
                    if(!scope.$$phase) {
                        scope.$apply();
                    }
                    if (page !== undefined) {
                        scrollToPage(page);
                    }
                    generatePages();
                });
            }

            function scrollToPage(page) {
                var body = $('html, body'),
                    elementSize = scope.$eval(attrs.elementSize),
                    containerWidth = $('.infinite-scroll > .content').width(),
                    perRow = Math.floor(containerWidth / elementSize.width),
                    top = (page-minLoadedOffset) / perRow * elementSize.height;
                body.animate({scrollTop: top}, 600, 'linear');
                calculateCurrentPage();
            }

            function prepareScrolling() {
                scrollDistance = 0;
                if (attrs.distance !== null) {
                    scope.$watch(attrs.distance, function(value) {
                        scrollDistance = parseInt(value, 10);
                        return scrollDistance;
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
            }

            function calculateCurrentPage() {
                var elementSize = scope.$eval(attrs.elementSize),
                    containerWidth = $('.infinite-scroll > .content').width(),
                    perRow = Math.floor(containerWidth / elementSize.width),
                    row = $window.scrollTop() / elementSize.height,
                    page = parseInt(row / (pageSize / perRow)) *
                        pageSize + scope.minLoadedOffset;
                scope.currentPage = page;
                if(!scope.$$phase) {
                    scope.$apply();
                }

                $location.search('offset', page);
            }

            function handler() {
                calculateCurrentPage();

                var elementBottom, remaining, shouldScroll, windowBottom;
                windowBottom = window.innerHeight + $window.scrollTop();
                elementBottom = elem.offset().top + elem.height();
                remaining = elementBottom - windowBottom;
                shouldScroll = remaining <= window.innerHeight * scrollDistance;

                if (shouldScroll && scrollEnabled &&
                        !scope.manualNextLoading && !scope.waitingForMore &&
                        !scope.bottomIsLoaded) {
                    scope.loadNext();
                } else if (shouldScroll) {
                    checkWhenEnabled = true;
                    return checkWhenEnabled;
                }
            }

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

angular.module('planevent').directive('offerpreview', function() {
    return {
        restrict: 'EA',
        scope: {
            'offer': '=offer',
        },
        templateUrl: 'assets/partials/directives/offerPreview.html',
    };
});
