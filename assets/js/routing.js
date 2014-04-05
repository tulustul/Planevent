'use strict';

angular.module('planevent').config(function($routeProvider) {
    $routeProvider
    // .when('/', {
    //     templateUrl: 'assets/partials/mainView.html',
    //     controller: 'MainPageController'
    // })
    .when('/', {
        templateUrl: 'assets/partials/homePage.html',
        controller: 'HomePageController'
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

    .when('/offers/search', {
        templateUrl: 'assets/partials/offersList.html',
        controller: 'OfferListController',
        reloadOnSearch: false
    })
    .when('/offer/:offerId', {
        templateUrl: 'assets/partials/offerPage.html',
        controller: 'OfferPageController'
    })

    .when('/offerAddEdit', {
        templateUrl: 'assets/partials/offerAddEdit/main.html',
        controller: 'OfferAddEditController'
    })
    .when('/offerAddEdit/:offerId', {
        templateUrl: 'assets/partials/offerAddEdit/main.html',
        controller: 'OfferAddEditController'
    })

    .otherwise({redirectTo: '/offers/search'});
});
