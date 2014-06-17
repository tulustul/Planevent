'use strict';

angular.module('planevent').controller('AccountController',
        function($scope, $location, accountService, authService,
                 categoriesService) {

    $scope.informationView = 'assets/partials/profile/information.html';
    $scope.settingsView = 'assets/partials/profile/settings.html';
    $scope.likingsView = 'assets/partials/profile/likings.html';
    $scope.changePasswordView = 'assets/partials/profile/changePassword.html';

    $scope.accountSaved = false;
    $scope.loggedUser = null;

    $scope.waiting = false;

    authService.getLoggedUser()
    .success(function(loggedUser) {

        $scope.loggedUser = loggedUser;

        if (loggedUser === undefined) {
            $location.path('/');
            return;
        }

        categoriesService.getCategories(function(categories) {
            var likingsIds = $scope.loggedUser.likingsIds;
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
        $scope.loggedUser = null;
        $location.path('/');
    };

    $scope.saveAccount = function() {
        $scope.accountSaved = false;
        accountService.saveAccount($scope.loggedUser, function(account) {
            $scope.loggedUser = account;
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
        function($scope) {

    $scope.addLiking = function(subcategory, level) {
        var likings = $scope.loggedUser.likings;
        likings[likings.length] = {
            subcategory: subcategory,
            level: level
        };
        subcategory.available = false;
    };

    $scope.removeLiking = function(liking) {
        var likings = $scope.loggedUser.likings;
        likings.splice(likings.indexOf(liking), 1);
        liking.subcategory.available = true;
    };

});