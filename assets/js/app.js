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
        ['$scope', '$location', '$rootScope', 'globalsService',
    function($scope, $location, $rootScope, globalsService) {
        $scope.categories = globalsService.categories;
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
        ['$scope', '$resource', '$routeParams', 'globalsService',
        function($scope, $resource, $routeParams, globalsService) {
    var Vendor = $resource('/api/vendor/:id');
    $scope.vendor = Vendor.get({id: $routeParams.vendorId});
    $scope.categories = globalsService.categories;

    $scope.removeVendor = function() {
        Vendor.remove({id: $scope.vendor.id});
    }

}]);

planevent.controller('VendorAddEditController',
    ['$scope', '$resource', '$routeParams', '$location', '$upload', 'globalsService',
    function($scope, $resource, $routeParams, $location, $upload, globalsService) {

        $scope.locationComplete = false;
        $scope.validatingLocation = false;
        $scope.categories = globalsService.categories;
        $scope.contactTypes = globalsService.contactTypes;
        $scope.vendorView = 'assets/partials/vendorPage.html';

        if ($routeParams.vendorId == undefined) {
            $scope.vendor = {gallery: []};
        } else {
            var Vendor = $resource('/api/vendor/:id');
            $scope.vendor = Vendor.get({id: $routeParams.vendorId}, function() {
                var address = $scope.vendor.address;
                $scope.locationComplete = address.city && address.street;
            });
        }

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
            addressString = address.street + ' ' + address.postal_code + ' ' + address.city;
            geocoder = new google.maps.Geocoder();
            geocoder.geocode({'address': addressString},
                function(results, status) {
                    $scope.validatingLocation = false;
                    if (status == google.maps.GeocoderStatus.OK) {
                        var location = results[0].geometry.location;
                        address.latitude = location.nb;
                        address.longitude = location.ob;
                        address.validated = true;
                    } else {
                        address.latitude = 0;
                        address.longitude = 0;
                        address.validated = false;
                    }
                    $scope.$apply();
                }
            );
        }

        $scope.addContact = function() {
            var contacts = $scope.vendor.contacts;
            if (contacts == undefined) {
                contacts = $scope.vendor.contacts = [];
            }
            contacts[contacts.length] = {};
        }

        $scope.removeContact = function(contactNo) {
            $scope.vendor.contacts.splice(contactNo, 1);
        }

        $scope.uploadLogo = function(files) {
            uploadImages(files, 'api/image', function(data) {
                $scope.vendor.logo = {path: data.path};
            });
        }

        $scope.uploadGallery = function(files) {
            uploadImages(files, 'api/gallery', function(data) {
                var gallery = $scope.vendor.gallery;
                gallery[gallery.length] = {path: data.path};
            });
        }

        function uploadImages(files, api, callback) {
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                $scope.upload = $upload.upload({
                    url: api,
                    method: 'POST',
                    // data: {myObj: $scope.myModelObj},
                    file: file,
                    // file: $files, //upload multiple files, this feature only works in HTML5 FromData browsers
                    /* set file formData name for 'Content-Desposition' header. Default: 'file' */
                    //fileFormDataName: myFile,
                    /* customize how data is added to formData. See #40#issuecomment-28612000 for example */
                    //formDataAppender: function(formData, key, val){}
                }).progress(function(evt) {
                    // console.log('percent: ' + parseInt(100.0 * evt.loaded / evt.total));
                }).success(function(data, status, headers, config) {
                    callback(data);
                });
                //.error(...)
                //.then(success, error, progress);
            }
        }

        $scope.goTo('info');
    }
]);

planevent.factory('globalsService', function($routeParams) {

    var lastCategoryId = -1;
    function makeCategory(name, icon, bindable) {
        if (bindable == undefined) {
            bindable = true;
        }
        lastCategoryId += 1;
        return {
            id: lastCategoryId,
            name: name,
            iconPath: '/static/images/icons/' + icon,
            bindable: bindable
        };
    }

    var lastContactTypeId = 0;
    function makeContactType(name) {
        lastContactTypeId += 1;
        return {
            id: lastContactTypeId,
            name: name
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
        contactTypes: [
            makeContactType('www'),
            makeContactType('email'),
            makeContactType('tel'),
            makeContactType('fax'),
            makeContactType('facebook')
        ]
    };
    return service;
});
