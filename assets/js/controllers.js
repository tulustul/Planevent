/*jshint camelcase: false */
'use strict';

angular.module('planevent').controller('MainPageController',
    function($scope, globalsService) {
        $scope.mainView = 'assets/partials/mainView.html';
        $scope.categoriesView = 'assets/partials/categoriesView.html';
        $scope.vendorView = 'assets/partials/vendorView.html';
        $scope.searchForm = 'assets/partials/search.html';
        $scope.loggedUserView = 'assets/partials/loggedUser.html';

        $scope.categories = globalsService.categories;
    }
);

angular.module('planevent').controller('CategoriesController',
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

angular.module('planevent').controller('VendorListController',
        function($scope, $location, $routeParams, $rootScope, searchService) {

    var LIMIT = 25;

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

angular.module('planevent').controller('VendorPageController',
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

angular.module('planevent').controller('VendorAddEditController',
    function($scope, $resource, $routeParams, $location, $upload,
             globalsService) {

        $scope.locationComplete = false;
        $scope.validatingLocation = false;
        $scope.categories = globalsService.categories;
        $scope.contactTypes = globalsService.contactTypes;
        $scope.vendorView = 'assets/partials/vendorView.html';

        if ($routeParams.vendorId === undefined) {
            $scope.vendor = {gallery: [], address: {}};
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

angular.module('planevent').controller('AdminPageController',
        function($scope, $resource) {

    $scope.vendorPromotionView = 'assets/partials/admin/vendorPromotion.html';
    $scope.categoriesView = 'assets/partials/admin/categories.html';
    $scope.subcategoriesView = 'assets/partials/admin/subcategories.html';
    $scope.statisticsView = 'assets/partials/admin/statistics.html';
    $scope.abTestsView = 'assets/partials/admin/abtests.html';
    $scope.databaseView = 'assets/partials/admin/database.html';

    var Vendor = $resource('/api/vendor/:id');
    var VendorPromotion = $resource('/api/vendor/:id/promotion/:promotion',
        {id:'@id', promotion: '@promotion'}
    );

    $scope.vendor = undefined;
    $scope.saved = false;
    $scope.vendorDoesNotExists = false;
    $scope.unknownError = false;


    $scope.resetMessages = function() {
        $scope.dangers = [];
        $scope.warnings = [];
        $scope.successes = [];

    };
    $scope.resetMessages();

    $scope.addDanger = function(msg) {
        $scope.dangers[$scope.dangers.length] = msg;
    };

    $scope.addWarning = function(msg) {
        $scope.warnings[$scope.warnings.length] = msg;
    };

    $scope.addSuccess = function(msg) {
        $scope.successes[$scope.successes.length] = msg;
    };

    $scope.getVendor = function(vendorId) {
        $scope.resetMessages();

        $scope.vendor = undefined;
        $scope.saved = false;
        $scope.unknownError = false;

        if (vendorId === '') {
            return;
        }

        $scope.vendor = Vendor.get({id: vendorId},
            function(){},
            function(response){
                $scope.vendor = undefined;
                if (response.status === 404) {
                    $scope.addDanger('Vendor does not exists!');
                } else {
                    $scope.addDanger('Unknown error');
                }
            }
        );
    };

    $scope.savePromotion = function(vendorId) {
        $scope.resetMessages();

        if ($scope.vendor === undefined) {
            return;
        }
        VendorPromotion.save({
                id: vendorId,
                promotion: $scope.vendor.promotion
            },
            function(){
                $scope.saved = true;
                $scope.addSuccess('Vendor saved');
            },
            function(response){
                if (response.status === 404) {
                    $scope.addDanger('Vendor does not exists!');
                } else {
                    $scope.addDanger('Unknown error');
                }
            }
        );
    };
});

angular.module('planevent').controller('RelatedVendorsController',
        function($scope, $resource) {

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

angular.module('planevent').controller('SearchController',
        function($scope, $location, searchService) {

    $scope.formVisible = false;
    $scope.tags = '';
    $scope.location = {};
    $scope.radius = 30;

    $scope.toogleSearch = function() {
        $scope.formVisible = !$scope.formVisible;
    };

    $scope.search = function() {
        searchService.resetParams();
        searchService.params.category = $scope.category;
        searchService.params.tags = $scope.tags;
        searchService.params.location = $scope.location.formatted;
        searchService.params.range = $scope.radius;

        $scope.clearVendors();
        $scope.loadMore();
    };
});

angular.module('planevent').controller('AccountController',
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

angular.module('planevent').controller('FirstLoggingController',
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

angular.module('planevent').controller('DatabaseManagementController',
        function($scope, $http, $timeout) {

    function countProgress(progressCounter) {
        $scope.taskState = 'Working';
        (function progress() {
            $http.get('api/task/' + progressCounter + '/progress')
                .success(function(response) {
                    $scope.task = response;
                    $scope.task.percentage =
                        ((response.progress / response.max) * 100)
                         .toFixed(1);

                    if ($scope.isWorking($scope.task)) {
                        $timeout(progress, 1000);
                    }
                });
        })();
    }

    $scope.isWorking = function(task) {
        if (task === undefined || task === null) {
            return false;
        }
        return task.status === 'PENDING' || task.status === 'WORKING';
    };

    $scope.cancelTask = function(task) {
        $scope.resetMessages();
        $http.post('/api/task/' + task.id + '/cancel')
            .success(function(msg) {
                    $scope.addSuccess(msg);
                })
            .error(function(msg) {
                    $scope.addDanger(msg);
                }
            );
    };

    $scope.updateSchema = function() {
        $scope.resetMessages();
        $http.post('/api/database/update')
            .success(function(msg) {
                    $scope.addSuccess(msg);
                })
            .error(function(msg) {
                    $scope.addDanger(msg);
                }
            );
    };

    $scope.clearDatabase = function() {
        $scope.resetMessages();
        $http.post('/api/database/clear')
            .success(function(msg) {
                    $scope.addSuccess(msg);
                })
            .error(function(msg) {
                    $scope.addDanger(msg);
                }
            );
    };

    $scope.generateRandomData = function(quantity) {
        var iquantity = parseInt(quantity);

        $scope.resetMessages();

        if (isNaN(iquantity)) {
            $scope.addDanger('Incorrect quantity: ' + quantity);
            return;
        }

        $http.post('/api/database/generate', iquantity)
            .success(function(response) {
                $scope.addSuccess(response.message);
                countProgress(response.progress_counter);
            })
            .error(function(msg) {
                $scope.addDanger(msg);
            });
    };

    $scope.export = function() {
        $scope.resetMessages();

        $http.get('/api/database/migration')
            .success(function(response) {
                $scope.addSuccess(response.message);
                countProgress(response.progress_counter);
            })
            .error(function(msg) {
                $scope.addDanger(msg);
            });
    };

    $scope.import = function() {
        $scope.resetMessages();

        $http.post('/api/database/migration')
            .success(function(response) {
                $scope.addSuccess(response.message);
                countProgress(response.progress_counter);
            })
            .error(function(msg) {
                $scope.addDanger(msg);
            });
    };

});