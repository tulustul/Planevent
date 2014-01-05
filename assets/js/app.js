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
    var Vendors = $resource('/api/vendors');
    $scope.vendors = Vendors.query();

    $scope.goToVendor = function(vendor) {
        $location.path('/vendor/' + vendor.id);
    }
}]);

planevent.controller('VendorPageController',
        ['$scope', '$resource', '$routeParams',
        function($scope, $resource, $routeParams) {
    var Vendor = $resource('/api/vendor/:id');
    $scope.vendor = Vendor.get({id: $routeParams.vendorId});
}]);
