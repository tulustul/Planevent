planevent.config(['$routeProvider', function($routeProvider) {$routeProvider

    .when('/vendors/:categoryId', {
        templateUrl: 'assets/partials/vendorsList.html',
        controller: 'VendorListController'})
    .when('/vendor/:vendorId', {
        templateUrl: 'assets/partials/vendorPage.html',
        controller: 'VendorPageController'})

    .when('/vendorAddEdit', {
        templateUrl: 'assets/partials/vendorAddEdit/main.html',
        controller: 'VendorAddEditController'})
    .when('/vendorAddEdit/:vendorId', {
        templateUrl: 'assets/partials/vendorAddEdit/main.html',
        controller: 'VendorAddEditController'})

    .otherwise({redirectTo: '/vendors/0'});
}]);

planevent.controller('MainPageController', ['$scope',
    function($scope) {
        $scope.categoriesView = 'assets/partials/categoriesView.html';
    }
]);

planevent.controller('CategoriesController',
        ['$scope', '$location', '$rootScope', 'CategoriesService',
    function($scope, $location, $rootScope, categoriesService) {
        $scope.categories = categoriesService.categories;
        $rootScope.selectedCategoryId = 0;

        $scope.searchCategory = function(categoryId) {
            $rootScope.selectedCategoryId = categoryId;
            $location.path('/vendors/' + categoryId);
        }
    }
]);

planevent.controller('VendorListController',
        ['$scope', '$resource', '$location', '$routeParams', '$rootScope',
        function($scope, $resource, $location, $routeParams, $rootScope) {

    var LIMIT = 15;

    $scope.currentOffset = 0;
    $scope.waitingForMore = false;
    $scope.noMoreData = false;
    $scope.vendors = [];

    $rootScope.selectedCategoryId = $routeParams.categoryId;

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

planevent.controller('VendorAddEditController',
    ['$scope', '$resource', '$routeParams', '$location', 'CategoriesService',
    function($scope, $resource, $routeParams, $location, categoriesService) {

        $scope.locationComplete = false;
        $scope.validatingLocation = false;

        if ($routeParams.vendorId == undefined) {
            $scope.vendor = {}
        } else {
            var Vendor = $resource('/api/vendor/:id');
            $scope.vendor = Vendor.get({id: $routeParams.vendorId}, function() {
                var address = $scope.vendor.address;
                $scope.locationComplete = address.city && address.street;
            });
        }
        $scope.categories = categoriesService.categories;

        $scope.goTo = function(section) {
            $scope.step = section;
            $scope.section = 'assets/partials/vendorAddEdit/'
                + section + '.html';
        }

        $scope.submit = function() {
            var Vendors = $resource('/api/vendors');
            var vendor = Vendors.save($scope.vendor , function() {
                $location.path('/vendor/' + vendor.id);
            });
        }

        $scope.validateAddress = function() {
            var address = $scope.vendor.address;
            if (!address.city || !address.street) {
                $scope.locationComplete = false;
                return;
            } else {
                $scope.locationComplete = true;
            }
            $scope.validatingLocation = true;
            addressString = address.street + ' ' + address.city + ' ' + address.postal_code;
            geocoder = new google.maps.Geocoder();
            geocoder.geocode({'address': addressString},
                function(results, status) {
                    $scope.validatingLocation = false;
                    if (status == google.maps.GeocoderStatus.OK) {
                        var location = results[0].geometry.location;
                        address.latitude = location.ob;
                        address.longitude = location.nb;
                        address.validated = true;
                    } else {
                        address.validated = false;
                    }
                    $scope.$apply();
                }
            );
        }

        $scope.goTo('info');
    }
]);

planevent.factory('CategoriesService', function($routeParams) {

    var lastId = -1;
    function makeCategory(name, icon, bindable) {
        if (bindable == undefined) {
            bindable = true;
        }
        lastId += 1;
        return {
            id: lastId,
            name: name,
            iconPath: '/static/images/icons/' + icon,
            bindable: bindable
        };
    }

    var service = {
        categories: [
            makeCategory('Wszystko', 'question.png', false),
            makeCategory('Hotele', 'question.png'),
            makeCategory('Catering', 'question.png'),
            makeCategory('Transport', 'question.png'),
            makeCategory('Sale', 'question.png'),
            makeCategory('Sport', 'question.png'),
            makeCategory('Inne', 'question.png')
        ],
    };
    return service;
});
