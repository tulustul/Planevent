planevent.config(['$routeProvider', function($routeProvider) {$routeProvider

    .when('/', {
        templateUrl: 'assets/partials/mainView.html',
        controller: 'MainPageController'})

    .when('/about', {
        templateUrl: 'assets/partials/about.html',
        controller: 'MainPageController'})
    .when('/terms', {
        templateUrl: 'assets/partials/term.html',
        controller: 'MainPageController'})
    .when('/faq', {
        templateUrl: 'assets/partials/faq.html',
        controller: 'MainPageController'})
    .when('/contact', {
        templateUrl: 'assets/partials/contact.html',
        controller: 'MainPageController'})

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

    .otherwise({redirectTo: '/'});
}]);

planevent.controller('MainPageController', ['$scope', 'globalsService',
    function($scope, globalsService) {
        $scope.mainView = 'assets/partials/mainView.html';
        $scope.categoriesView = 'assets/partials/categoriesView.html';
        $scope.vendorView = 'assets/partials/vendorView.html';
        $scope.searchForm = 'assets/partials/search.html';

        $scope.categories = globalsService.categories;
    }
]);

planevent.controller('CategoriesController',
        ['$scope', '$location', '$routeParams',
    function($scope, $location, $routeParams) {
        $scope.selectedCategory = $scope.categories[$routeParams.categoryId];

        $scope.searchCategory = function(categoryId) {
            if (categoryId != undefined) {
                $scope.selectedCategory = $scope.categories[categoryId];
            }
            $location.path('/vendors/' + $scope.selectedCategory.id);
        }
    }
]);

planevent.controller('VendorListController',
        ['$scope', '$location', '$routeParams', '$rootScope', 'searchService',
        function($scope, $location, $routeParams, $rootScope, searchService) {

    var LIMIT = 15;

    searchService.resetParams();
    searchService.params.category = $routeParams.categoryId;

    $scope.goToVendor = function(vendor) {
        $location.path('/vendor/' + vendor.id);
    }

    $scope.clearVendors = function() {
        $scope.vendors = [];
        $scope.waitingForMore = false;
        $scope.noMoreData = false;
    }

    $scope.loadMore = function() {
        if ($scope.waitingForMore || $scope.noMoreData) {
            return;
        }
        $scope.waitingForMore = true;

        searchService.loadMore(LIMIT, function(moreVendors) {
            if (moreVendors.length == 0) {
                $scope.noMoreData = true;
            }
            $scope.vendors = _.union($scope.vendors, moreVendors);
            $scope.waitingForMore = false;
        });
    }
    $scope.clearVendors();
    $scope.loadMore();
}]);

planevent.controller('VendorPageController',
        ['$scope', '$resource', '$routeParams', 'globalsService',
        function($scope, $resource, $routeParams, globalsService) {
    var Vendor = $resource('/api/vendor/:id');
    $scope.vendorDoesNotExists = false;
    $scope.otherError = false;
    var vendor = Vendor.get({id: $routeParams.vendorId},
        function(){
            $scope.fetched = true;
            $scope.vendor = vendor;
        },
        function(response){
            if (response.status === 404) {
                $scope.vendorDoesNotExists = true;
            } else {
                $scope.otherError = true;
            }
        }
    );
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
        $scope.vendorView = 'assets/partials/vendorView.html';

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

        $scope.addTag = function() {
            var tags = $scope.vendor.tags;
            if (tags == undefined) {
                tags = $scope.vendor.tags = [];
            }
            tags[tags.length] = {};
        }

        $scope.removeTag = function(tagNo) {
            $scope.vendor.tags.splice(tagNo, 1);
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
                    file: file,
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

planevent.controller('AdminPageController',
        ['$scope', '$resource',
        function($scope, $resource) {

    var Vendor = $resource('/api/vendor/:id');
    var VendorPromotion = $resource('/api/vendor/:id/promotion/:promotion',
        {id:'@id', promotion: '@promotion'}
    );

    $scope.vendor = undefined;
    $scope.vendorId = undefined;
    $scope.saved = false;
    $scope.vendorDoesNotExists = false;
    $scope.unknownError = false;

    $scope.getVendor = function() {
        $scope.saved = false;
        $scope.vendorDoesNotExists = false;
        $scope.unknownError = false;
        $scope.vendor = Vendor.get({id: $scope.vendorId},
            function(){},
            function(response){
                $scope.vendor = undefined;
                if (response.status === 404) {
                    $scope.vendorDoesNotExists = true;
                } else {
                    $scope.unknownError = true;
                }
            }
        );
    }

    $scope.savePromotion = function() {
        if ($scope.vendor == undefined) {
            return;
        }
        VendorPromotion.save({
                id: $scope.vendorId,
                promotion: $scope.vendor.promotion
            },
            function(){
                $scope.saved = true;
            },
            function(response){
                if (response.status === 404) {
                    $scope.vendorDoesNotExists = true;
                } else {
                    $scope.unknownError = true;
                }
            }
        );
    }
}]);

planevent.controller('RelatedVendorsController',
        ['$scope', '$resource', '$location',
        function($scope, $resource, $location) {

    var VendorsSearch = $resource('/api/vendors/search');

    $scope.$watch('vendor', function() {
        if ($scope.vendor == undefined) {
            return;
        }

        tags_ids = _.map($scope.vendor.tags, function(tag) {
            return tag.id;
        })

        var params = {
            category: $scope.vendor.category,
            exclude_vendor_id: $scope.vendor.id,
            tags: tags_ids,
            range: 50,
            limit: 5
        };

        params.location = $scope.vendor.address.city;

        $scope.relatedVendors = VendorsSearch.query(params);
    });


    $scope.goToVendor = function(vendor) {
        $location.path('/vendor/' + vendor.id);
    }
}]);

planevent.controller('SearchController',
        ['$scope', '$location', 'searchService',
        function($scope, $location, searchService) {

    $scope.formVisible = false;
    $scope.tags = '';
    $scope.location = '';
    $scope.range = 50;

    $scope.toogleSearch = function() {
        $scope.formVisible = !$scope.formVisible;
    };

    $scope.search = function() {
        searchService.resetParams();
        searchService.params.category = $scope.category;
        searchService.params.tags = $scope.tags;
        searchService.params.location = $scope.location;
        searchService.params.range = $scope.range;

        $scope.clearVendors();
        $scope.loadMore();
    };
}]);


planevent.service('searchService', ['$resource', function($resource) {

    this.Vendors = $resource('/api/vendors/search');

    this.resetParams = function() {
        this.params = {
            category: 0,
            tags: [],
            location: '',
            range: 50,
            offset: 0,
            limit: 15,
        }
    }
    this.resetParams();

    this.loadMore = function(quantity, callback) {
        this.params.limit = quantity;
        var moreVendors = this.Vendors.query(this.params, function() {
            callback(moreVendors);
        });
        this.params.offset += quantity
    }
}]);
