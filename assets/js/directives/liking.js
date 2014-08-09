'use strict';

angular.module('planevent').directive('liking', function() {
    return {
        restrict: 'EA',
        require: '^ngModel',
        templateUrl: 'assets/partials/directives/liking.html',
        link: function($scope, element, attrs) {

            function processLiking(liking) {
                switch (liking.level) {
                    case 1:
                        smileIcon  = 'frown-o';
                        break;
                    case 2:
                        smileIcon = 'meh-o';
                        break;
                    case 3:
                        smileIcon = 'smile-o';
                        break;
                    case 4:
                        smileIcon = 'heart';
                        break;
                    default:
                        smileIcon = 'meh-o';
                        break;
                }

                $scope.smileIcon = smileIcon;
                $scope.liking = liking;
            }

            var liking = $scope.$eval(attrs.ngModel),
                smileIcon;

            processLiking(liking);

            $scope.$on('likingUpdated', function(event, updatedLiking) {
                if (updatedLiking.id === liking.id) {
                    processLiking(liking);
                }
            });
        }
    };
});
