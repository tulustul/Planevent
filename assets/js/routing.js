'use strict';

angular.module('planevent').config(
        function($locationProvider, $routeProvider) {

    $locationProvider.html5Mode(true);

    $routeProvider
    .when('/password_recall_callback', {
        templateUrl: 'assets/partials/passwordRecallCallback.html',
        controller: 'PasswordRecallCallbackController'
    })
    // .when('/', {
    //     templateUrl: 'assets/partials/homePage.html',
    //     controller: 'HomePageController'
    // })
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

    .when('/user', {
        redirectTo: '/user/informations'
    })
    .when('/user/informations', {
        templateUrl: 'assets/partials/user/informations.html',
        controller: 'ProfileInformationsController'
    })
    .when('/user/settings', {
        templateUrl: 'assets/partials/user/settings.html',
        controller: 'ProfileSettingsController'
    })
    .when('/user/changePassword', {
        templateUrl: 'assets/partials/user/changePassword.html',
        controller: 'ProfileChangePasswordController'
    })
    .when('/user/likings', {
        templateUrl: 'assets/partials/user/likings.html',
        controller: 'ProfileLikingsController'
    })
    .when('/user/firstLogging', {
        templateUrl: 'assets/partials/user/firstLogging.html',
        controller: 'FirstLoggingController'
    })

    .when('/offers/search', {
        templateUrl: 'assets/partials/offers/offersList.html',
        controller: 'OfferListController',
        reloadOnSearch: false
    })
    .when('/offers/:offerId', {
        templateUrl: 'assets/partials/offer/offerPage.html',
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
