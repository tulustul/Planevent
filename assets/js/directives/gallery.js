'use strict';

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
