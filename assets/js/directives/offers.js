'use strict';

angular.module('planevent').directive('offerpreview', function() {
    return {
        restrict: 'EA',
        scope: {
            'offer': '=offer',
        },
        templateUrl: 'assets/partials/directives/offerPreview.html',
    };
});
