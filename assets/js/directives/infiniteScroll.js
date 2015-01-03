'use strict';

/* Basing on ng-infinite-scroll - v1.0.0 */
angular.module('planevent').directive('infinitescroll',
        function($rootScope, $timeout, $location, $routeParams) {

    return {
        restrict: 'EA',
        scope: '=',
        transclude: true,
        templateUrl: 'assets/partials/directives/infiniteScroll.html',

        link: function(scope, elem, attrs) {
            var autoScroolLimit = parseInt(attrs.autoScrollLimit),
                fetchFunction = scope.$eval(attrs.fetchFunction),
                element = $(attrs.scrollingElement),
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
                maxLoadedOffset = minLoadedOffset;
                fetchEntities(minLoadedOffset, pageSize, function(entities) {
                    scope.entities = entities;
                    maxLoadedOffset += entities.length;
                    return 0;
                });
            }
            scope[attrs.resetFunctionName] = reset;

            function calculatePageSize() {
                var elementSize = scope.$eval(attrs.elementSize),
                    isMobile = $(window).width() <= 600,
                    scrollingElement = isMobile ? $(window) : element,
                    containerHeight = scrollingElement.height(),
                    fetchPages = parseInt(attrs.fetchPages);

                pageSize = parseInt(
                    (containerHeight * fetchPages) / elementSize
                );
            }

            // pages disabled for now
            // function generatePages() {
            //     scope.pages = _.range(0, scope.totalCount, pageSize);
            // }

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
                    // pages disabled for now
                    // generatePages();
                });
            }

            function scrollToPage(page) {
                var body = $('html, body'),
                    elementSize = scope.$eval(attrs.elementSize),
                    containerWidth = $('.infinite-scroll > .content').width(),
                    perRow = Math.floor(containerWidth / elementSize.width),
                    top = (page-minLoadedOffset) / perRow * elementSize.height;
                body.animate({scrollTop: top}, 600, 'linear');
                calculateCurrentElement();
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

            function calculateCurrentElement() {
                var elementSize = scope.$eval(attrs.elementSize),
                    isMobile = $(window).width() <= 600,
                    scrollingElement = isMobile ? $(window) : element,
                    row = scrollingElement.scrollTop() / elementSize,
                    page = parseInt(row + scope.minLoadedOffset);

                scope.currentPage = page;

                if (!scope.$$phase) {
                    scope.$apply();
                }

                $location.search('offset', page);
            }

            function handlerMobile() {
                var elementBottom = (
                    element.offset().top + element.height()
                ),
                    windowScroll = $(window).height() + $(window).scrollTop(),
                    remaining = elementBottom - windowScroll;

                return(remaining <= $(window).height() * scrollDistance);
            }

            function handlerDesktop() {
                var elementBottom, remaining, windowBottom;

                windowBottom = (
                    element.innerHeight() +
                    element.scrollTop()
                );
                elementBottom = (
                    element.offset().top +
                    element[0].scrollHeight
                );
                remaining = elementBottom - windowBottom;

                return (
                    remaining <= element.innerHeight() * scrollDistance
                );
            }

            function handler() {
                var isMobile = $(window).width() <= 600,
                    scrollHandler = isMobile ? handlerMobile : handlerDesktop,
                    shouldScroll = scrollHandler();

                calculateCurrentElement();

                if (shouldScroll && scrollEnabled &&
                        !scope.manualNextLoading && !scope.waitingForMore &&
                        !scope.bottomIsLoaded) {
                    scope.loadNext();
                } else if (shouldScroll) {
                    checkWhenEnabled = true;
                    return checkWhenEnabled;
                }
            }

            element.on('scroll', handler);
            $(window).on('scroll', handler);
            scope.$on('$destroy', function() {
                element.off('scroll', handler);
                $(window).off('scroll', handler);
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
