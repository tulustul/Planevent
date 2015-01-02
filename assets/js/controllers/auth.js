'use strict';

angular.module('planevent').service('userProfileService',
        function($location, authService, accountService, toastService) {

    this.prepareScope = function(scope) {
        authService.getLoggedUser(function(account) {
            scope.account = account;
            if (account === undefined || account === 'null') {
                $location.path('/');
                return;
            }
        });

        scope.saveAccount = function() {
            scope.saving = true;
            accountService.saveAccount(scope.account, function() {
                scope.saving = false;
                toastService.info('Zapisano zmiany');
            });
        };
    };
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
        function($scope, $rootScope, $mdDialog, authService, toastService) {

    $scope.cancel = $mdDialog.cancel;

    $scope.showRemindPasswordForm = function() {
        $mdDialog.show({
            templateUrl: 'assets/partials/auth/remindPasswordModal.html',
            controller: 'RemindPasswordController',
        });
    };

    $scope.showRegistrationForm = function() {
        $mdDialog.show({
            templateUrl: 'assets/partials/auth/registrationModal.html',
            controller: 'RegistrationController',
        });
    };

    $scope.login = function(email, password) {
        $scope.waiting = true;
        $scope.message = '';

        authService.login(email, password)
        .success(function(account) {
            $scope.waiting = false;
            $rootScope.$broadcast('loggedIn', account);
            $mdDialog.hide();
        })
        .error(function(response) {
            $scope.waiting = false;
            if (response.message === 'invalid_credentials') {
                toastService.warn('Niepoprawne hasło');
            }
        });
    };
});

angular.module('planevent').controller('RegistrationController',
        function($scope, $rootScope, $mdDialog, authService, toastService) {

    $scope.cancel = $mdDialog.cancel;

    $scope.register = function(email, password, passwordRepeat) {
        $scope.message = '';

        if (password !== passwordRepeat) {
            toastService.warn('Hasła nie są identyczne');
            return;
        }

        $scope.waiting = true;

        authService.register(email, password, passwordRepeat)
        .success(function(account) {
            $scope.waiting = false;
            $rootScope.$broadcast('loggedIn', account);
            $mdDialog.hide();
        })
        .error(function(response) {
            $scope.waiting = false;
            if (response.message === 'invalid_credentials') {
                toastService.warn('Niepoprawne hasło');
            }
        });
    };

});

angular.module('planevent').controller('RemindPasswordController',
        function($scope, $mdDialog, authService, toastService) {

    $scope.cancel = $mdDialog.cancel;

    $scope.remindPassword = function(email) {
        $scope.waiting = true;

        authService.sendRecallEmail(email)
        .success(function(response) {
            $scope.waiting = false;
            if (response.message === 'mail_sent') {
                toastService.info('E-mail z przypomnieniem został wysłany');
            }
        })
        .error(function(response) {
            $scope.waiting = false;
            if (response.message === 'invalid_email') {
                toastService.warn('Niepoprawny e-mail');
            } else {
                toastService.error(
                    'Wystąpił błąd podczas wysyłania przypomnienia'
                );
            }
        });
    };
});

angular.module('planevent').controller('UserSidebarController',
        function($scope, $rootScope, $mdSidenav, authService) {

    $scope.close = function() {
        $mdSidenav('userSidebar').close();
    };

    $scope.logout = function() {
        authService.logout(function() {
            $rootScope.$broadcast('loggedOut');
            $mdSidenav('userSidebar').close();
        });
    };
});
