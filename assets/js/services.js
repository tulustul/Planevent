'use strict';

planevent.service('searchService', function($resource) {

    this.Vendors = $resource('/api/vendors/search');

    this.resetParams = function() {
        this.params = {
            category: 0,
            tags: [],
            location: '',
            range: 50,
            offset: 0,
            limit: 15,
        };
    };
    this.resetParams();

    this.loadMore = function(quantity, callback) {
        this.params.limit = quantity;
        var moreVendors = this.Vendors.query(this.params, function() {
            callback(moreVendors);
        });
        this.params.offset += quantity;
    };
});

planevent.service('accountService', function($resource) {

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

planevent.factory('globalsService',
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
