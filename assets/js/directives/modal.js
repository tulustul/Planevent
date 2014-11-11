'use strict';

angular.module('planevent').directive('modal', function() {
    return {
        restrict: 'EA',
        templateUrl: 'assets/partials/directives/modal.html',
        transclude: true,

        link: function($scope, element, attrs) {
        	$scope.title = attrs.title;
        }
    };
});
