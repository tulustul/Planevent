'use strict';

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
                if (attrs.infiniteScrollDisabled !== undefined) {
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
