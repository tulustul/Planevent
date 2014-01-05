planevent.config(['$routeProvider', function($routeProvider) {$routeProvider
    .when('/', {
        templateUrl: 'assets/partials/vendorsList.html',
        controller: 'VendorListController'})
    .when('/vendor/:vendorId', {
        templateUrl: 'assets/partials/vendorPage.html',
        controller: 'VendorPageController'})
    .otherwise({redirectTo: '/'});
}]);

planevent.controller('VendorListController',
        ['$scope', '$resource', '$location',
        function($scope, $resource, $location) {

    var LIMIT = 15;

    $scope.currentOffset = 0;
    $scope.waitingForMore = false;
    $scope.noMoreData = false;
    $scope.vendors = [];

    var Vendors = $resource('/api/vendors');

    $scope.goToVendor = function(vendor) {
        $location.path('/vendor/' + vendor.id);
    }

    $scope.loadMore = function() {
        if ($scope.waitingForMore || $scope.noMoreData) {
            return;
        }
        $scope.waitingForMore = true;
        $scope.currentOffset += LIMIT;
        var moreVendors = Vendors.query({
            limit: LIMIT,
            offset: $scope.currentOffset
        }, function() {
            if (moreVendors.length == 0) {
                $scope.noMoreData = true;
            }
            $scope.vendors = _.union($scope.vendors, moreVendors);
            $scope.waitingForMore = false;
        });
    }
    $scope.loadMore();
}]);

planevent.controller('VendorPageController',
        ['$scope', '$resource', '$routeParams',
        function($scope, $resource, $routeParams) {
    var Vendor = $resource('/api/vendor/:id');
    $scope.vendor = Vendor.get({id: $routeParams.vendorId});
}]);
