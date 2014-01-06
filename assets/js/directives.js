planevent.directive('addressviewer', function() {
    return {
        restrict: 'EA',
        // require: 'longitude, latitude',
        // scope: {
        //   ngModel: '='
        // },
        templateUrl: 'assets/partials/directives/addressViewer.html',
        link: function(scope, element, attrs) {
            function updateMap() {
                var latitude = scope.$eval(attrs.latitude);
                var longitude = scope.$eval(attrs.longitude);

                var mapOptions = {
                    center: new google.maps.LatLng(
                        latitude, longitude),
                    zoom: 10
                };
                var mapElement = $(element, '.address-viewer');
                var map = new google.maps.Map(mapElement, mapOptions);
            }

            updateMap();

            scope.$watch(latitude, updateMap);
            scope.$watch(longitude, updateMap);
        }
    }
});
