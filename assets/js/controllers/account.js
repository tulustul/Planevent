'use strict';

angular.module('planevent').service('userProfileService',
        function($location, authService) {

    this.prepareScope = function(scope) {
        scope.userProfileNavigation =
            'assets/partials/profile/userProfileNavigation.html';

        authService.getLoggedUser()
        .success(function(loggedUser) {

            scope.loggedUser = loggedUser;

            if (loggedUser === undefined || loggedUser === 'null') {
                $location.path('/');
                return;
            }
        });
    };
});

angular.module('planevent').controller('AccountController',
        function($scope, $location, userProfileService, accountService,
         authService) {
    $scope.loggedUser = null;

    $scope.waiting = false;

    userProfileService.prepareScope($scope);

    $scope.$on('loggedIn', function(event, account) {
        $scope.loggedUser = account;
    });

    $scope.logout = function() {
        authService.logout();
        $scope.loggedUser = null;
        $location.path('/');
    };
});

angular.module('planevent').controller('ProfileInformationsController',
        function($scope, userProfileService) {

    userProfileService.prepareScope($scope);
});

angular.module('planevent').controller('ProfileSettingsController',
        function($scope, userProfileService) {

    userProfileService.prepareScope($scope);

});

angular.module('planevent').controller('ProfileChangePasswordController',
        function($scope, userProfileService, authService) {

    userProfileService.prepareScope($scope);

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

angular.module('planevent').controller('ProfileLikingsController',
        function($scope, $http, userProfileService, categoriesService) {

    userProfileService.prepareScope($scope);

    categoriesService.getCategories(function(categories) {
        $scope.categories = categories;
    });

    $scope.setLiking = function(liking, level) {
        liking.level = level;

        $http.post('/api/accounts/liking/' + liking.id + '/level', level)
        .success(function() {
            $scope.$broadcast('likingUpdated', liking);
        })
        .error(function() {
            // nothing?
        });

    };
});

angular.module('planevent').controller('FirstLoggingController',
        function($scope, $location, userProfileService) {

    userProfileService.prepareScope($scope);

    $scope.likingsView = 'assets/partials/profile/likings.html';
});
