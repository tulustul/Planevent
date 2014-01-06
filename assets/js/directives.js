planevent.directive('addressviewer', function() {
    return {
        restrict: 'EA',
        require: '^ngModel',
        templateUrl: 'assets/partials/directives/addressViewer.html',
        link: function(scope, element, attrs) {
            function updateMap() {
                var address = scope.$eval(attrs.ngModel);

                if (address && address.validated) {
                    var position = new google.maps.LatLng(
                            address.latitude, address.longitude);
                    var zoom = 13;
                } else {
                    var position = new google.maps.LatLng(52, 19);
                    var zoom = 5;
                }

                var mapOptions = {
                    center: position,
                    zoom: zoom
                };

                var mapElement = $('.address-viewer', element)[0];
                var map = new google.maps.Map(mapElement, mapOptions);

                if (address.validated) {
                    var marker = new google.maps.Marker({
                        position: mapOptions.center,
                        map: map,
                        title: address.street + ', ' + address.city
                    });
                }
            }

            scope.$watchCollection(
                '[vendor.address.longitude, vendor.address.latitude]',
                updateMap);
        }
    }
});
