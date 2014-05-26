'use strict';

angular.module('planevent').controller('FirstLoggingController',
        function($scope, $location, accountService) {

    accountService.getAccount(function(loggedUser) {
        if (loggedUser === undefined) {
            $location.path('/');
        } else if (loggedUser.login_count > 1) {
            $location.path('/userProfile');
        }
    });
});

angular.module('planevent').controller('PasswordRecallCallbackController',
        function($scope, $routeParams, authService) {

    $scope.password = '';

    $scope.changePassword = function(password) {
        $scope.waiting = true;

        authService.changePasswordFromToken($routeParams.token, password)
        .success(function(response) {
            $scope.waiting = false;
            $scope.message = response.message;
        })
        .error(function(response) {
            $scope.waiting = false;
            $scope.message = response.message;
        });
    };
});

angular.module('planevent').controller('LoginController',
        function($scope, $rootScope, authService) {

    $scope.email = '';
    $scope.password = '';
    $scope.message = '';
    $scope.form = '';
    $scope.waiting = false;
    $scope.registration = false;

    $scope.login = function(email, password) {
        $scope.waiting = true;
        $scope.message = '';

        authService.login(email, password)
        .success(function(account) {
            $scope.waiting = false;
            $rootScope.loggedUser = account;
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

    $scope.register = function(email, password) {
        $scope.waiting = true;
        $scope.message = '';

        authService.register(email, password)
        .success(function(account) {
            $scope.waiting = false;
            $rootScope.loggedUser = account;
        })
        .error(function(response) {
            $scope.waiting = false;
            $scope.message = response.message;
        });
    };
});
