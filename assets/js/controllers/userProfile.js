'use strict';

angular.module('planevent').controller('AccountController',
        function($scope, $location, $rootScope, accountService, authService,
                 globalsService) {

    $scope.informationView = 'assets/partials/profile/information.html';
    $scope.settingsView = 'assets/partials/profile/settings.html';
    $scope.likingsView = 'assets/partials/profile/likings.html';
    $scope.changePasswordView = 'assets/partials/profile/changePassword.html';

    $scope.accountSaved = false;
    $rootScope.loggedUser = null;

    $scope.waiting = false;

    authService.getLoggedUser()
    .success(function(loggedUser) {

        $rootScope.loggedUser = loggedUser;

        if (loggedUser === undefined) {
            $location.path('/');
            return;
        }

        globalsService.getCategories(function(categories) {
            var likingsIds = $rootScope.loggedUser.likingsIds;
            $scope.availableCategories = _.map(categories, function(c) {
                // TODO list of ids instead of field injection
                c.available = true;
                c.subcategories = _.map(c.subcategories, function(sub) {
                    sub.available = likingsIds.indexOf(sub.id) === -1;
                    return sub;
                });
                return c;
            });
        });
    });

    $scope.logout = function() {
        authService.logout();
        $rootScope.loggedUser = null;
        $location.path('/');
    };

    $scope.saveAccount = function() {
        $scope.accountSaved = false;
        accountService.saveAccount($rootScope.loggedUser, function(account) {
            $rootScope.loggedUser = account;
        });
        $scope.accountSaved = true;
    };

    $scope.changePassword = function(oldPassword, newPassword) {
        $scope.waiting = true;

        authService.changePassword(oldPassword, newPassword)
        .success(function(response) {
            $scope.message = response.message;
            $scope.waiting = false;
        })
        .error(function(response) {
            $scope.waiting = false;
            $scope.message = response.message;
        });


    };
});

angular.module('planevent').controller('LikingsEditionController',
        function($scope, $location, accountService) {

    $scope.addLiking = function(subcategory, level) {
        var likings = $rootScope.loggedUser.likings;
        likings[likings.length] = {
            subcategory: subcategory,
            level: level
        };
        subcategory.available = false;
    };

    $scope.removeLiking = function(liking) {
        var likings = $rootScope.loggedUser.likings;
        likings.splice(likings.indexOf(liking), 1);
        liking.subcategory.available = true;
    };

});