'use strict';

angular.module('planevent').service('userProfileService',
        function($location, authService) {

    this.prepareScope = function(scope) {
        scope.userProfileNavigation =
            'assets/partials/profile/userProfileNavigation.html';

        authService.getLoggedUser(function(account) {
            scope.account = account;
            if (account === undefined || account === 'null') {
                $location.path('/');
                return;
            }
        });
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

// angular.module('planevent').controller('LoginController',
//         function($scope, $rootScope, authService) {

//     $scope.email = '';
//     $scope.password = '';
//     $scope.message = '';
//     $scope.form = '';
//     $scope.waiting = false;
//     $scope.registration = false;

//     $scope.login = function(email, password) {
//         $scope.waiting = true;
//         $scope.message = '';

//         authService.login(email, password)
//         .success(function(account) {
//             $scope.waiting = false;
//             $rootScope.$broadcast('loggedIn', account);
//             authService.loggedUser = account;
//         })
//         .error(function(response) {
//             $scope.waiting = false;
//             $scope.message = response.message;
//         });
//     };

//     $scope.register = function(email, password) {
//         $scope.waiting = true;
//         $scope.message = '';

//         authService.register(email, password)
//         .success(function(account) {
//             $scope.waiting = false;
//             $rootScope.$broadcast('loggedIn', account);
//         })
//         .error(function(response) {
//             $scope.waiting = false;
//             $scope.message = response.message;
//         });
//     };
// });

angular.module('planevent').controller('LoginController',
        function($scope, $rootScope, $mdDialog, authService) {

    $scope.close = $mdDialog.hide;

    $scope.showRemindPasswordForm = function() {
        $mdDialog.show({
            templateUrl: 'assets/partials/auth/remindPasswordModal.html',
            controller: 'RemindPasswordController',
        });
    };

    $scope.showRegistrationForm = function() {
        $scope.$broadcast('showRegistrationForm');
    };

    $scope.login = function(email, password) {
        $scope.waiting = true;
        $scope.message = '';

        authService.login(email, password)
        .success(function(account) {
            $scope.waiting = false;
            $rootScope.$broadcast('loggedIn', account);
            authService.loggedUser = account;
            $mdDialog.hide();
        })
        .error(function(response) {
            $scope.waiting = false;
            $scope.message = response.message;
        });
    };
});

angular.module('planevent').controller('RegistrationController',
        function($scope, $rootScope, $mdDialog, authService) {

    $scope.close = $mdDialog.hide;

    $scope.register = function(email, password, passwordRepeat) {
        $scope.waiting = true;
        $scope.message = '';

        if (password !== passwordRepeat) {
            // $scope.registrationForm.password.$error.dontMatch = true;
            $scope.passwordRepeat.$setValidity(false);
            return;
        }

        authService.register(email, password, passwordRepeat)
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

angular.module('planevent').controller('RemindPasswordController',
        function($scope, $mdDialog, authService) {

    $scope.close = $mdDialog.hide;

    $scope.remindPassword = function(email) {
        $scope.waiting = true;

        authService.sendRecallEmail(email)
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

angular.module('planevent').controller('UserSidebarController',
        function($scope, $rootScope, $mdSidenav, authService) {

    $scope.close = function() {
        $mdSidenav('userSidebar').close();
    }

    $scope.logout = function() {
        authService.logout(function() {
            $rootScope.$broadcast('loggedOut');
            $mdSidenav('userSidebar').close();
        });
    };
});

