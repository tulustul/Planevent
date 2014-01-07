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

planevent.directive('gallery', function() {
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
                    $scope._Index = ($scope._Index > 0) ? --$scope._Index : $scope.gallery.length - 1;
                };

                $scope.showNext = function () {
                    $scope._Index = ($scope._Index < $scope.gallery.length - 1) ? ++$scope._Index : 0;
                };

                $scope.showPhoto = function (index) {
                    $scope._Index = index;
                };
            }

            $scope.$watchCollection('vendor', init);
        }
    }
});
