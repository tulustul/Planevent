'use strict';

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
