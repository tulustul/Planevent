planevent.config(['$routeProvider', function($routeProvider) {$routeProvider
    .when('/vendors/:categoryId', {
        templateUrl: 'assets/partials/vendorsList.html',
        controller: 'VendorListController'})
    .when('/vendor/:vendorId', {
        templateUrl: 'assets/partials/vendorPage.html',
        controller: 'VendorPageController'})
    .when('/addVendor', {
        templateUrl: 'assets/partials/addVendorPage.html',
        controller: 'AddVendorController'})
    .otherwise({redirectTo: '/vendors/0'});
}]);

planevent.controller('MainPageController', ['$scope',
    function($scope) {
        $scope.categoriesView = 'assets/partials/categoriesView.html';
    }
]);

planevent.controller('CategoriesController',
        ['$scope', '$location', 'CategoriesService',
    function($scope, $location, categoriesService) {
        $scope.categories = categoriesService.categories;
        $scope.selectedCategoryId = categoriesService.selectedCategoryId;

        $scope.searchCategory = function(categoryId) {
            $scope.selectedCategoryId = categoryId;
            categoriesService.selectedCategoryId = categoryId;
            $location.path('/vendors/' + categoryId);
        }
    }
]);

planevent.controller('VendorListController',
        ['$scope', '$resource', '$location', '$routeParams',
        function($scope, $resource, $location, $routeParams) {

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
        var moreVendors = Vendors.query({
            category: $routeParams.categoryId,
            limit: LIMIT,
            offset: $scope.currentOffset
        }, function() {
            if (moreVendors.length == 0) {
                $scope.noMoreData = true;
            }
            $scope.vendors = _.union($scope.vendors, moreVendors);
            $scope.waitingForMore = false;
        });
        $scope.currentOffset += LIMIT;
    }
    $scope.loadMore();
}]);

planevent.controller('VendorPageController',
        ['$scope', '$resource', '$routeParams', 'CategoriesService',
        function($scope, $resource, $routeParams, categoriesService) {
    var Vendor = $resource('/api/vendor/:id');
    $scope.vendor = Vendor.get({id: $routeParams.vendorId});
    $scope.categories = categoriesService.categories;
}]);

planevent.controller('AddVendorController',
        ['$scope', '$resource', '$routeParams',
        function($scope, $resource, $routeParams) {
}]);

planevent.factory('CategoriesService', function($routeParams) {

    function makeCategory(name, icon) {
        return {
            name: name,
            iconPath: '/static/images/icons/' + icon
        };
    }

    var service = {
        categories: [
            makeCategory('Wszystko', 'question.png'),
            makeCategory('Hotele', 'question.png'),
            makeCategory('Catering', 'question.png'),
            makeCategory('Transport', 'question.png'),
            makeCategory('Sale', 'question.png'),
            makeCategory('Sport', 'question.png')
        ],

        selectedCategoryId: parseInt($routeParams.categoryId)
    };
    return service;
});