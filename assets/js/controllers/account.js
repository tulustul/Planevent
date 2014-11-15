'use strict';

angular.module('planevent').controller('ProfileInformationsController',
        function($scope, userProfileService) {

    userProfileService.prepareScope($scope);
});

angular.module('planevent').controller('ProfileSettingsController',
        function($scope, userProfileService, accountService) {

    userProfileService.prepareScope($scope);

    $scope.saveAccount = function() {
        accountService.saveAccount($scope.loggedUser, function() {
            $scope.saved = true;
        });
    };

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

        liking.waiting = true;
        $http.post('/api/accounts/liking/' + liking.id + '/level', level)
        .success(function() {
            $scope.$broadcast('likingUpdated', liking);
            liking.waiting = false;
        })
        .error(function() {
            liking.waiting = false;
        });

    };
});

angular.module('planevent').controller('FirstLoggingController',
        function($scope, $location, userProfileService) {

    userProfileService.prepareScope($scope);

    $scope.likingsView = 'assets/partials/profile/likings.html';
});
