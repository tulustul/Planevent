/*jshint camelcase: false */
'use strict';

angular.module('planevent').controller('HomePageController',
    function($scope) {
        $scope.registrationLandingPage =
            'assets/partials/registrationLandingPage.html';
        $scope.promotedView = 'assets/partials/promotedView.html';
    }
);

angular.module('planevent').controller('MainPageController',
    function($scope, globalsService) {
        $scope.mainView = 'assets/partials/mainView.html';
        $scope.categoriesView = 'assets/partials/categoriesView.html';
        $scope.offerView = 'assets/partials/offerView.html';
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
            $location.path('/offers/' + $scope.selectedCategory.id);
        };
    }
);

angular.module('planevent').controller('OfferListController',
        function($scope, $location, $routeParams, searchService) {

    searchService.resetParams();
    searchService.params.category = $routeParams.categoryId;

    $scope.goToOffer = function(offer) {
        $location.path('/offer/' + offer.id);
    };

    $scope.offerPreviewSize = function() {
        var previewElem = $('.offer-preview-wrapper').first();
        if (previewElem.length === 0) {
            return {width: 1, height: 1};
        }
        return {
            width: previewElem.outerWidth(true),
            height: previewElem.outerHeight(true)
        };
    };

    $scope.fetch = function(offset, limit, callback) {
        searchService.fetch(offset, limit, callback);
    };
});

angular.module('planevent').controller('OfferPageController',
        function($scope, $resource, $routeParams, globalsService) {
    var Offer = $resource('/api/offer/:id');
    $scope.offerDoesNotExists = false;
    $scope.otherError = false;
    var offer = Offer.get({id: $routeParams.offerId},
        function(){
            $scope.fetched = true;
            $scope.offer = offer;
        },
        function(response){
            if (response.status === 404) {
                $scope.offerDoesNotExists = true;
            } else {
                $scope.otherError = true;
            }
        }
    );
    $scope.categories = globalsService.categories;

    $scope.removeOffer = function() {
        Offer.remove({id: $scope.offer.id});
    };

});

angular.module('planevent').controller('OfferAddEditController',
    function($scope, $resource, $routeParams, $location, $upload,
             globalsService) {

        $scope.locationComplete = false;
        $scope.validatingLocation = false;
        $scope.categories = globalsService.categories;
        $scope.contactTypes = globalsService.contactTypes;
        $scope.offerView = 'assets/partials/offerView.html';

        if ($routeParams.offerId === undefined) {
            $scope.offer = {gallery: [], address: {}};
        } else {
            var Offer = $resource('/api/offer/:id');
            $scope.offer = Offer.get({id: $routeParams.offerId}, function() {
                var address = $scope.offer.address;
                $scope.locationComplete = address.city && address.street;
            });
        }

        $scope.goTo = function(section) {
            $scope.step = section;
            $scope.section = 'assets/partials/offerAddEdit/' +
                section + '.html';
        };

        $scope.submit = function() {
            var Offers = $resource('/api/offers');
            var offer = Offers.save($scope.offer , function() {
                $location.path('/offer/' + offer.id);
            });
        };

        $scope.addContact = function() {
            var contacts = $scope.offer.contacts;
            if (contacts === undefined) {
                contacts = $scope.offer.contacts = [];
            }
            contacts[contacts.length] = {};
        };

        $scope.removeContact = function(contactNo) {
            $scope.offer.contacts.splice(contactNo, 1);
        };

        $scope.addTag = function() {
            var tags = $scope.offer.tags;
            if (tags === undefined) {
                tags = $scope.offer.tags = [];
            }
            tags[tags.length] = {};
        };

        $scope.removeTag = function(tagNo) {
            $scope.offer.tags.splice(tagNo, 1);
        };

        $scope.uploadLogo = function(files) {
            uploadImages(files, 'api/image', function(data) {
                $scope.offer.logo = {path: data.path};
            });
        };

        $scope.uploadGallery = function(files) {
            uploadImages(files, 'api/gallery', function(data) {
                var gallery = $scope.offer.gallery;
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

    $scope.offerPromotionView = 'assets/partials/admin/offerPromotion.html';
    $scope.categoriesView = 'assets/partials/admin/categories.html';
    $scope.subcategoriesView = 'assets/partials/admin/subcategories.html';
    $scope.statisticsView = 'assets/partials/admin/statistics.html';
    $scope.abTestsView = 'assets/partials/admin/abtests.html';
    $scope.databaseView = 'assets/partials/admin/database.html';

    var Offer = $resource('/api/offer/:id');
    var OfferPromotion = $resource('/api/offer/:id/promotion/:promotion',
        {id:'@id', promotion: '@promotion'}
    );

    $scope.offer = undefined;
    $scope.saved = false;
    $scope.offerDoesNotExists = false;
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

    $scope.getOffer = function(offerId) {
        $scope.resetMessages();

        $scope.offer = undefined;
        $scope.saved = false;
        $scope.unknownError = false;

        if (offerId === '') {
            return;
        }

        $scope.offer = Offer.get({id: offerId},
            function(){},
            function(response){
                $scope.offer = undefined;
                if (response.status === 404) {
                    $scope.addDanger('Offer does not exists!');
                } else {
                    $scope.addDanger('Unknown error');
                }
            }
        );
    };

    $scope.savePromotion = function(offerId) {
        $scope.resetMessages();

        if ($scope.offer === undefined) {
            return;
        }
        OfferPromotion.save({
                id: offerId,
                promotion: $scope.offer.promotion
            },
            function(){
                $scope.saved = true;
                $scope.addSuccess('Offer saved');
            },
            function(response){
                if (response.status === 404) {
                    $scope.addDanger('Offer does not exists!');
                } else {
                    $scope.addDanger('Unknown error');
                }
            }
        );
    };
});

angular.module('planevent').controller('RelatedOffersController',
        function($scope, $resource) {

    var OffersSearch = $resource('/api/offers/search');

    $scope.$watch('offer', function() {
        if ($scope.offer === undefined) {
            return;
        }

        var tags_ids = _.map($scope.offer.tags, function(tag) {
            return tag.id;
        });

        var params = {
            category: $scope.offer.category.id,
            exclude_offer_id: $scope.offer.id,
            tags: tags_ids,
            range: 50,
            limit: 5
        };

        params.location = $scope.offer.address.city;

        $scope.relatedOffers = OffersSearch.query(params);
    });

});

angular.module('planevent').controller('SearchController',
        function($scope, $location, $http, $routeParams, searchService) {

    $scope.categoryEnabled = false;
    $scope.locationEnabled = false;
    $scope.priceEnabled = false;

    $scope.tags = '';
    $scope.location = {};
    $scope.radius = 30;
    $scope.priceRange = [0, 200];

    if ('price_min' in $routeParams) {
        $scope.priceEnabled = true;
        $scope.priceRange[0] = parseInt($routeParams.price_min);
    }
    if ('price_max' in $routeParams) {
        $scope.priceEnabled = true;
        $scope.priceRange[1] = parseInt($routeParams.price_max);
    }
    if ('category' in $routeParams) {
        $scope.categoryEnabled = true;
        $scope.category = parseInt($routeParams.category);
    }
    // if ('lat' in $routeParams && 'lon' in $routeParams &&
            // 'location' in $routeParams) {
    if ('location' in $routeParams) {
        $scope.locationEnabled = true;
        $scope.location.formatted = $routeParams.location;
        // $scope.location.latitude = $routeParams.lat;
        // $scope.location.longitude = $routeParams.lon;
    }
    if ('range' in $routeParams) {
        $scope.radius = $routeParams.range;
        // $scope.location.latitude = $routeParams.lat;
        // $scope.location.longitude = $routeParams.lon;
    }

    $scope.searchTags = [];
    $http.get('api/tags/names').success(function(tags) {
        $scope.searchTags = tags;
    });

    $scope.toogleSearch = function() {
        $scope.formVisible = !$scope.formVisible;
    };

    $scope.search = function(resetOffset) {
        searchService.resetParams();

        searchService.categoryEnabled = $scope.categoryEnabled;
        searchService.locationEnabled = $scope.locationEnabled;
        searchService.priceEnabled = $scope.priceEnabled;

        // searchService.params.tags = $scope.tags;

        if ($scope.categoryEnabled) {
            searchService.params.category = $scope.category;
        }

        if ($scope.locationEnabled) {
            searchService.params.location = $scope.location.formatted;
            searchService.params.range = $scope.radius;
        }

        if ($scope.priceEnabled) {
            searchService.params.price_min = $scope.priceRange[0];
            searchService.params.price_max = $scope.priceRange[1];
        }
        $location.search(searchService.params);

        $scope.resetSearch(resetOffset);
    };
    $scope.search(false);
});

angular.module('planevent').controller('AccountController',
        function($scope, $location, accountService, authService,
                 globalsService) {

    $scope.informationView = 'assets/partials/profile/information.html';
    $scope.settingsView = 'assets/partials/profile/settings.html';
    $scope.likingsView = 'assets/partials/profile/likings.html';

    $scope.accountSaved = false;
    $scope.loggedUser = null;

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

    $scope.logout = function() {
        authService.logout();
        $scope.loggedUser = null;
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


angular.module('planevent').controller('RegistrationController',
        function($scope, authService) {

    $scope.email = '';
    $scope.password = '';

    $scope.register = function(email, password) {
        authService.register(email, password);
    };
});


angular.module('planevent').controller('LoginController',
        function($scope, authService) {

    $scope.email = '';
    $scope.password = '';
    $scope.message = '';
    $scope.form = '';
    $scope.waiting = false;

    $scope.login = function(email, password) {
        $scope.waiting = true;
        $scope.message = '';

        authService.login(email, password)
        .success(function(account) {
            $scope.waiting = false;
            $scope.loggedUser = account;
        })
        .error(function(response) {
            $scope.waiting = false;
            $scope.message = response.message;
        });
    };

    $scope.sendRecallEmail = function(email) {
        $scope.waiting = true;

        authService.sendRecallEmail(email)
        .success(function(response) {
            $scope.waiting = false;
            $scope.showLoginForm = true;
            $scope.showRecallForm = false;
            $scope.message = response.message;
        })
        .error(function(response) {
            $scope.waiting = false;
            $scope.message = response.message;
        });
    };
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

    $scope.migrations = {
        'import': {
            name: 'import',
            exec: function(spreadsheetName, worksheetName) {
                $scope.resetMessages();

                $http.post('/api/database/migration', {
                    spreadsheet: spreadsheetName,
                    worksheet: worksheetName,
                })
                .success(function(response) {
                    $scope.addSuccess(response.message);
                    countProgress(response.progress_counter);
                })
                .error(function(msg) {
                    $scope.addDanger(msg);
                });
            }
        },
        'export': {
            name: 'export',
            exec: function() {
                $scope.resetMessages();

                $http.get('/api/database/migration')
                .success(function(response) {
                    $scope.addSuccess(response.message);
                    countProgress(response.progress_counter);
                })
                .error(function(msg) {
                    $scope.addDanger(msg);
                });
            }
        }
    };

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
});
