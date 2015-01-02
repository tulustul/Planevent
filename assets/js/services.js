'use strict';

angular.module('planevent').service('searchService',
        function($http, $resource) {

    this.Offers = $resource('/api/offers/search');

    this.resetParams = function() {
        // this.categoryEnabled = false;
        // this.locationEnabled = false;
        // this.priceEnabled = false;
        // this.excludeIdEnabled = false;
        this.params = {};
    };
    this.resetParams();

    this.fetch = function(offset, limit, callback) {
        var params = {offset: offset, limit: limit},
            response;

        if (this.params.category) {
            params.category = this.params.category;
        }

        if (this.params.location && this.params.range) {
            params.location = this.params.location;
            params.range = this.params.range;
        }

        if (this.params.price_min || this.params.price_max) {
            params.price_min = this.params.price_min;
            params.price_max = this.params.price_max;
        }

        if (this.params.exclude_offer_id) {
            params.exclude_offer_id = this.params.exclude_offer_id;
        }

        response = this.Offers.get(params, function() {
            callback(response.total_count, response.offers);
        });
    };

});

angular.module('planevent').service('offersService',
    function($resource, $http) {

    this.getPromotedOffers = function() {
        return $http.get('/api/offers/promoted');
    };

    this.getRecommendations = function() {
        return $http.get('/api/offers/recommendations');
    };
});

angular.module('planevent').service('authService',
        function($http, $location) {

    var self = this;
    this.loggedUser = null;
    this.waitingForResponse = false;
    this.callbacksQueue = [];

    this.getLoggedUser = function(callback) {
        if (self.waitingForResponse) {
            self.callbacksQueue[self.callbacksQueue.length] = callback;
            return;
        }
        if (this.loggedUser === null) {
            self.waitingForResponse = true;
            $http.get('/api/user/logged')
            .success(function(loggedUser) {
                self.waitingForResponse = false;
                self.loggedUser = loggedUser;
                if (self.loggedUser === 'null') {
                    self.loggedUser = null;
                }
                callback(self.loggedUser);
                _.each(self.callbacksQueue, function(callback) {
                    callback(self.loggedUser);
                });
                self.callbacksQueue = [];
            })
            .error(function(){
                self.waitingForResponse = false;
            });
        } else {
            callback(self.loggedUser);
        }
    };

    this.register = function(email, password) {
        return $http.post('/api/register', email + ':' + password)
        .success(function(account) {
            self.loggedUser = account;
        });
    };

    this.login = function(email, password) {
        return $http.post('/api/login', email + ':' + password)
        .success(function(account) {
            self.loggedUser = account;
        });
    };

    this.logout = function(callback) {
        $http.post('/api/logout')
        .success(function() {
            self.loggedUser = null;
            $location.path('/');
            callback();
        });
    };

    this.sendRecallEmail = function(email) {
        return $http.post('/api/recall_password', email);
    };

    this.changePassword = function(oldPassword, newPassword) {
        return $http.post(
            '/api/change_password',
            oldPassword + ':' + newPassword
        );
    };

    this.changePasswordFromToken = function(token, password) {
        return $http.post(
            '/api/recall_password_callback',
            token + ':' + password
        );
    };
});

angular.module('planevent').service('accountService', function($resource) {

    var LoggedUser = $resource('/api/user/logged');

    function computeLikedSubcategoriesIds(account) {
        account.likingsIds = _.map(account.likings, function(liking) {
            return liking.subcategory.id;
        });
    }

    function restCallback(account, callback) {
        if (account.id === undefined) {
            account = undefined;
            return;
        }
        computeLikedSubcategoriesIds(account);
        callback(account);
    }

    this.saveAccount = function(account, callback) {
        var loggedUser = LoggedUser.save(account, function() {
            restCallback(loggedUser, callback);
        });
    };
});

angular.module('planevent').factory('categoriesService',
    function($routeParams, $resource) {

    var Categories = $resource('/api/categories');

    var lastContactTypeId = 0;
    function makeContactType(name) {
        lastContactTypeId += 1;
        return {
            id: lastContactTypeId,
            name: name
        };
    }

    var service = {
        categories: Categories.query(),
        contactTypes: [
            makeContactType('www'),
            makeContactType('email'),
            makeContactType('tel'),
            makeContactType('fax'),
            makeContactType('facebook')
        ]
    };

    service.getCategories = function(callback) {
        if (service.categories === undefined) {
            service.categories = Categories.query({}, function() {
                callback(service.categories);
            });
        } else {
            callback(service.categories);
        }
    };

    service.getCategoryById = function(categoryId) {
        if (service.categories === undefined) {
            console.error(
                'Cannot call getCategoryById withour categories fetched'
            );
        }
        var filtered = _.filter(service.categories, function(category) {
            return category.id === categoryId;
        });
        if (filtered.length > 0) {
            return filtered[0];
        } else {
            return null;
        }
    };

    return service;
});

angular.module('planevent').service('fileUploadService',
        function($upload) {

    this.upload = function(files, api, callback) {
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            $upload.upload({
                url: api,
                method: 'POST',
                file: file,
            // }).progress(function(evt) {
                // console.log('percent: ' + parseInt(100.0 *
                               //evt.loaded / evt.total));
            }).success(callback);
            //.error(...)
            //.then(success, error, progress);
        }
    };
});

angular.module('planevent').service('toastService',
        function($mdToast) {

    this.info = function(message) {
        this.show(message, 'infoToast.html');
    }

    this.warn = function(message) {
        this.show(message, 'warnToast.html');
    }

    this.error = function(message) {
        this.show(message, 'errorToast.html');
    }

    this.show = function(message, template) {
        $mdToast.show({
            controller: 'ToastController',
            templateUrl: 'assets/partials/widgets/' + template,
            hideDelay: 5000,
            position: 'bottom right',
            locals: {
                message: message,
            },
        });
    };
});
