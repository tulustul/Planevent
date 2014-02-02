/*jshint camelcase: false */
'use strict';

planevent.controller('MainPageController',
    function($scope, globalsService) {
        $scope.mainView = 'assets/partials/mainView.html';
        $scope.categoriesView = 'assets/partials/categoriesView.html';
        $scope.vendorView = 'assets/partials/vendorView.html';
        $scope.searchForm = 'assets/partials/search.html';
        $scope.loggedUserView = 'assets/partials/loggedUser.html';

        $scope.categories = globalsService.categories;
    }
);

planevent.controller('CategoriesController',
    function($scope, $location, $routeParams) {
        var categoryId = parseInt($routeParams.categoryId);
        for (var i in $scope.categories) {
            var category = $scope.categories[i];
            if (category.id === categoryId) {
                $scope.selectedCategory = category;
                break;
            }
        }

        $scope.searchCategory = function(category) {
            if (category !== undefined) {
                $scope.selectedCategory = category;
            }
            $location.path('/vendors/' + $scope.selectedCategory.id);
        };
    }
);

planevent.controller('VendorListController',
        function($scope, $location, $routeParams, $rootScope, searchService) {

    var LIMIT = 15;

    searchService.resetParams();
    searchService.params.category = $routeParams.categoryId;

    $scope.goToVendor = function(vendor) {
        $location.path('/vendor/' + vendor.id);
    };

    $scope.clearVendors = function() {
        $scope.vendors = [];
        $scope.waitingForMore = false;
        $scope.noMoreData = false;
    };

    $scope.loadMore = function() {
        if ($scope.waitingForMore || $scope.noMoreData) {
            return;
        }
        $scope.waitingForMore = true;

        searchService.loadMore(LIMIT, function(moreVendors) {
            if (moreVendors.length < LIMIT) {
                $scope.noMoreData = true;
            }
            $scope.vendors = _.union($scope.vendors, moreVendors);
            $scope.waitingForMore = false;
        });
    };
    $scope.clearVendors();
    $scope.loadMore();
});

planevent.controller('VendorPageController',
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
    };

});

planevent.controller('VendorAddEditController',
    function($scope, $resource, $routeParams, $location, $upload,
             globalsService) {

        $scope.locationComplete = false;
        $scope.validatingLocation = false;
        $scope.categories = globalsService.categories;
        $scope.contactTypes = globalsService.contactTypes;
        $scope.vendorView = 'assets/partials/vendorView.html';

        if ($routeParams.vendorId === undefined) {
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
            $scope.section = 'assets/partials/vendorAddEdit/' +
                section + '.html';
        };

        $scope.submit = function() {
            var Vendors = $resource('/api/vendors');
            var vendor = Vendors.save($scope.vendor , function() {
                $location.path('/vendor/' + vendor.id);
            });
        };

        $scope.addContact = function() {
            var contacts = $scope.vendor.contacts;
            if (contacts === undefined) {
                contacts = $scope.vendor.contacts = [];
            }
            contacts[contacts.length] = {};
        };

        $scope.removeContact = function(contactNo) {
            $scope.vendor.contacts.splice(contactNo, 1);
        };

        $scope.addTag = function() {
            var tags = $scope.vendor.tags;
            if (tags === undefined) {
                tags = $scope.vendor.tags = [];
            }
            tags[tags.length] = {};
        };

        $scope.removeTag = function(tagNo) {
            $scope.vendor.tags.splice(tagNo, 1);
        };

        $scope.uploadLogo = function(files) {
            uploadImages(files, 'api/image', function(data) {
                $scope.vendor.logo = {path: data.path};
            });
        };

        $scope.uploadGallery = function(files) {
            uploadImages(files, 'api/gallery', function(data) {
                var gallery = $scope.vendor.gallery;
                gallery[gallery.length] = {path: data.path};
            });
        };

        function uploadImages(files, api, callback) {
            function successHandler(data) { //, status, headers, config
                callback(data);
            }

            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                $scope.upload = $upload.upload({
                    url: api,
                    method: 'POST',
                    file: file,
                // }).progress(function(evt) {
                    // console.log('percent: ' + parseInt(100.0 *
                                   //evt.loaded / evt.total));
                }).success(successHandler);
                //.error(...)
                //.then(success, error, progress);
            }
        }

        $scope.goTo('info');
    }
);

planevent.controller('AdminPageController',
        function($scope, $resource) {

    $scope.vendorPromotionView = 'assets/partials/admin/vendorPromotion.html';
    $scope.categoriesView = 'assets/partials/admin/categories.html';
    $scope.subcategoriesView = 'assets/partials/admin/subcategories.html';
    $scope.statisticsView = 'assets/partials/admin/statistics.html';

    var Vendor = $resource('/api/vendor/:id');
    var VendorPromotion = $resource('/api/vendor/:id/promotion/:promotion',
        {id:'@id', promotion: '@promotion'}
    );

    $scope.vendor = undefined;
    $scope.saved = false;
    $scope.vendorDoesNotExists = false;
    $scope.unknownError = false;

    $scope.getVendor = function(vendorId) {
        $scope.vendor = undefined;
        $scope.saved = false;
        $scope.vendorDoesNotExists = false;
        $scope.unknownError = false;

        if (vendorId === '') {
            return;
        }

        $scope.vendor = Vendor.get({id: vendorId},
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
    };

    $scope.savePromotion = function(vendorId) {
        if ($scope.vendor === undefined) {
            return;
        }
        VendorPromotion.save({
                id: vendorId,
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
    };
});

planevent.controller('RelatedVendorsController',
        function($scope, $resource, $location) {

    var VendorsSearch = $resource('/api/vendors/search');

    $scope.$watch('vendor', function() {
        if ($scope.vendor === undefined) {
            return;
        }

        var tags_ids = _.map($scope.vendor.tags, function(tag) {
            return tag.id;
        });

        var params = {
            category: $scope.vendor.category.id,
            exclude_vendor_id: $scope.vendor.id,
            tags: tags_ids,
            range: 50,
            limit: 5
        };

        params.location = $scope.vendor.address.city;

        $scope.relatedVendors = VendorsSearch.query(params);
    });

});

planevent.controller('SearchController',
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
});

planevent.controller('AccountController',
        function($scope, $location, accountService, globalsService) {

    $scope.informationView = 'assets/partials/profile/information.html';
    $scope.settingsView = 'assets/partials/profile/settings.html';
    $scope.likingsView = 'assets/partials/profile/likings.html';

    $scope.accountSaved = false;

    accountService.getAccount(function(loggedUser) {
        $scope.loggedUser = loggedUser;

        if (loggedUser === undefined) {
            $location.path('/');
            return;
        }

        globalsService.getCategories(function(categories) {
            var likingsIds = $scope.loggedUser.likingsIds;
            $scope.availableCategories = _.map(categories, function(c) {
                // TODO list of ids instead of field injection
                c.available = true;
                c.subcategories = _.map(c.subcategories, function(sub) {
                    sub.available = likingsIds.indexOf(sub.id) === -1;
                    return sub;
                });
                return c;
            });
        });
    });

    $scope.goToProfile = function() {
        $location.path('/userProfile');
    };

    $scope.saveAccount = function() {
        $scope.accountSaved = false;
        accountService.saveAccount($scope.loggedUser, function(account) {
            $scope.loggedUser = account;
        });
        $scope.accountSaved = true;
    };

    $scope.addLiking = function(subcategory, level) {
        var likings = $scope.loggedUser.likings;
        likings[likings.length] = {
            subcategory: subcategory,
            level: level
        };
        subcategory.available = false;
    };

    $scope.removeLiking = function(liking) {
        var likings = $scope.loggedUser.likings;
        likings.splice(likings.indexOf(liking), 1);
        liking.subcategory.available = true;
    };
});

planevent.controller('FirstLoggingController',
        function($scope, $location, accountService) {

    accountService.getAccount(function(loggedUser) {
        $scope.loggedUser = loggedUser;

        if (loggedUser === undefined) {
            $location.path('/');
        } else if (loggedUser.login_count > 1) {
            $location.path('/userProfile');
        }
    });
});
