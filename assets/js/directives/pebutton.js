'use strict';

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
                if ('target' in attrs) {
                    $('a', element).attr('target', attrs.target);
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
