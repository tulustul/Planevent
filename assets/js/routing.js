'use strict';

angular.module('planevent').config(function($routeProvider) {
    $routeProvider
    .when('/', {
        templateUrl: 'assets/partials/mainView.html',
        controller: 'MainPageController'
    })
    .when('/playground', {
        templateUrl: 'assets/partials/playground.html',
        controller: 'MainPageController'
    })

    .when('/about', {
        templateUrl: 'assets/partials/about.html',
        controller: 'MainPageController'
    })
    .when('/terms', {
        templateUrl: 'assets/partials/term.html',
        controller: 'MainPageController'
    })
    .when('/faq', {
        templateUrl: 'assets/partials/faq.html',
        controller: 'MainPageController'
    })
    .when('/contact', {
        templateUrl: 'assets/partials/contact.html',
        controller: 'MainPageController'
    })

    .when('/userProfile', {
        templateUrl: 'assets/partials/userProfile.html',
        controller: 'AccountController'
    })
    .when('/userProfile/firstLogging', {
        templateUrl: 'assets/partials/profile/firstLogging.html',
        controller: 'FirstLoggingController'
    })

    .when('/vendors/:categoryId', {
        templateUrl: 'assets/partials/vendorsList.html',
        controller: 'VendorListController'
    })
    .when('/vendor/:vendorId', {
        templateUrl: 'assets/partials/vendorPage.html',
        controller: 'VendorPageController'
    })

    .when('/vendorAddEdit', {
        templateUrl: 'assets/partials/vendorAddEdit/main.html',
        controller: 'VendorAddEditController'
    })
    .when('/vendorAddEdit/:vendorId', {
        templateUrl: 'assets/partials/vendorAddEdit/main.html',
        controller: 'VendorAddEditController'
    })

    .otherwise({redirectTo: '/'});
});
