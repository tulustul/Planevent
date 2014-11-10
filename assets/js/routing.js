'use strict';

angular.module('planevent').config(
        function($locationProvider, $routeProvider) {

    $locationProvider.html5Mode(true);

    $routeProvider
    // .when('/', {
    //     templateUrl: 'assets/partials/mainView.html',
    //     controller: 'MainPageController'
    // })
    .when('/password_recall_callback', {
        templateUrl: 'assets/partials/passwordRecallCallback.html',
        controller: 'PasswordRecallCallbackController'
    })
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
        redirectTo: '/userProfile/informations'
    })
    .when('/userProfile/informations', {
        templateUrl: 'assets/partials/profile/informations.html',
        controller: 'ProfileInformationsController'
    })
    .when('/userProfile/settings', {
        templateUrl: 'assets/partials/profile/settings.html',
        controller: 'ProfileSettingsController'
    })
    .when('/userProfile/changePassword', {
        templateUrl: 'assets/partials/profile/changePassword.html',
        controller: 'ProfileChangePasswordController'
    })
    .when('/userProfile/likings', {
        templateUrl: 'assets/partials/profile/likings.html',
        controller: 'ProfileLikingsController'
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
