'use strict';

angular.module('planevent').directive('compareTo', function() {
    return {
        require: 'ngModel',
        replace: false,
        link: function(scope, element, attributes, ngModel) {
            var compareTo = attributes.compareTo;
            ngModel.$validators.compareTo = function(modelValue) {
                return modelValue === scope.$eval(compareTo);
            };

            scope.$watch('otherModelValue', function() {
                ngModel.$validate();
            });
        }
    };
});
