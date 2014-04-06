'use strict';

angular.module('planevent').service('searchService',
        function($http, $resource) {

    this.Offers = $resource('/api/offers/search');

    this.resetParams = function() {
        this.categoryEnabled = false;
        this.locationEnabled = false;
        this.priceEnabled = false;
        this.params = {};
    };
    this.resetParams();

    this.fetch = function(offset, limit, callback) {
        var params = {offset: offset, limit: limit},
            response;

        if (this.categoryEnabled) {
            params.category = this.params.category;
        }

        if (this.locationEnabled) {
            params.location = this.params.location;
            params.range = this.params.range;
        }

        if (this.priceEnabled) {
            params.price_min = this.params.price_min;
            params.price_max = this.params.price_max;
        }

        response = this.Offers.get(params, function() {
            callback(response.total_count, response.offers);
        });
    };

});

angular.module('planevent').service('authService', function($http) {

    var self = this;
    this.loggedUser = null;

    this.register = function(email, password) {
        $http.post('/api/register', email + ':' + password)
        .success(function(response) {
            alert(JSON.stringify(response));
        })
        .error(function(response) {
            alert(JSON.stringify(response));
        });
    };

    this.login = function(email, password) {
        return $http.post('/api/login', email + ':' + password)
        .success(function(account) {
            self.loggedUser = account;
        });
    };

    this.logout = function() {
        $http.post('/api/logout')
        .success(function() {
            self.loggedUser = null;
        })
        .error(function(response) {
            alert(JSON.stringify(response));
        });
    };

    this.sendRecallEmail = function(email) {
        return $http.post('/api/recall_password', email);
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

    this.getAccount = function(callback) {
        var loggedUser = LoggedUser.get({}, function() {
            restCallback(loggedUser, callback);
        });
    };

    this.saveAccount = function(account, callback) {
        var loggedUser = LoggedUser.save(account, function() {
            restCallback(loggedUser, callback);
        });
    };
});

angular.module('planevent').factory('globalsService',
    function($routeParams, $resource) {

    var Categories = $resource('/api/categories');
    var Subcategories = $resource('/api/subcategories');

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
        subcategories: Subcategories.query(),
        contactTypes: [
            makeContactType('www'),
            makeContactType('email'),
            makeContactType('tel'),
            makeContactType('fax'),
            makeContactType('facebook')
        ]
    };

    service.getCategories = function(callback) {
        var categories = Categories.query({}, function() {
            callback(categories);
        });
    };

    return service;
});
