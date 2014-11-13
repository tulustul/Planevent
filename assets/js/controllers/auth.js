'use strict';

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
            $rootScope.$broadcast('loggedIn', account);
            authService.loggedUser = account;
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
            $rootScope.$broadcast('loggedIn', account);
        })
        .error(function(response) {
            $scope.waiting = false;
            $scope.message = response.message;
        });
    };
});

angular.module('planevent').controller('LoginController',
        function($scope, $modal) {

    $scope.showRemindPasswordForm = function() {
        var remindPasswordScope = $scope.$new(true);
        remindPasswordScope.modal = $modal.open({
            templateUrl: 'assets/partials/auth/remindPasswordModal.html',
            scope: remindPasswordScope,
            windowClass: 'remindPasswordModal',
            controller: 'RemindPasswordController',
        });
    };

    $scope.showRegistrationForm = function() {
        $scope.$emit('showRegistrationForm');
    };
});

angular.module('planevent').controller('RegistrationController',
        function($scope) {

});

angular.module('planevent').controller('RemindPasswordController',
        function($scope, authService) {

    $scope.remindPassword = function(email) {
        $scope.waiting = true;

        authService.sendRecallEmail(email)
        .success(function(response) {
            $scope.waiting = false;
            // $scope.showLoginForm = true;
            // $scope.showRecallForm = false;
            $scope.message = response.message;
        })
        .error(function(response) {
            $scope.waiting = false;
            $scope.message = response.message;
        });
    };
});
