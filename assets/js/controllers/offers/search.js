'use strict';

angular.module('planevent').controller('SearchController',
        function($scope, $location, $http, $routeParams, searchService) {

    $scope.categoryEnabled = false;
    $scope.locationEnabled = false;
    $scope.priceEnabled = false;

    $scope.tags = '';
    $scope.location = {};
    $scope.radius = 30;
    $scope.priceRange = [0, 200];

    if ('price_min' in $routeParams) {
        $scope.priceEnabled = true;
        $scope.priceRange[0] = parseInt($routeParams.price_min);
    }
    if ('price_max' in $routeParams) {
        $scope.priceEnabled = true;
        $scope.priceRange[1] = parseInt($routeParams.price_max);
    }
    if ('category' in $routeParams) {
        $scope.categoryEnabled = true;
        $scope.category = parseInt($routeParams.category);
    }
    if ('location' in $routeParams) {
        $scope.locationEnabled = true;
        $scope.location.formatted = $routeParams.location;
    }
    if ('range' in $routeParams) {
        $scope.radius = $routeParams.range;
    }

    $scope.searchTags = [];
    $http.get('api/tags/names').success(function(tags) {
        $scope.searchTags = tags;
    });

    $scope.isOnSearchPage = function() {
        return $location.path() === '/offers/search';
    };

    $scope.toogleSearch = function() {
        $scope.formVisible = !$scope.formVisible;
    };

    $scope.search = function(resetOffset) {

        searchService.params = {};

        if ($scope.categoryEnabled) {
            searchService.params.category = $scope.category;
        }

        if ($scope.locationEnabled) {
            searchService.params.location = $scope.location.formatted;
            searchService.params.range = $scope.radius;
        }

        if ($scope.priceEnabled) {
            searchService.params.price_min = $scope.priceRange[0];
            searchService.params.price_max = $scope.priceRange[1];
        }

        if (!$scope.isOnSearchPage()) {
            $location.path('/offers/search');
        } else {
            $scope.resetSearch(resetOffset);
        }
        $location.search(searchService.params);
    };
    if ($scope.isOnSearchPage()) {
        $scope.search(false);
    }
});