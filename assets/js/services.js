'use strict';

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
}]);

planevent.service('accountService', ['$resource', function($resource) {

    var LoggedUser = $resource('/api/user/logged');

    this.getAccount = function(callback) {
        var loggedUser = LoggedUser.get({}, function() {
            if (loggedUser.id === undefined) {
                loggedUser = undefined;
            }
            callback(loggedUser);
        });
    };
}]);

planevent.factory('globalsService',
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
    return service;
});
