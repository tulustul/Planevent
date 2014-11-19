'use strict';

angular.module('planevent').controller('UserNavigationController',
		function($scope, $routeParams, $location) {

	$scope.pages = [
		{
			label: 'Profil',
			template: 'assets/partials/user/profile.html',
			url: 'profile',
		},
		{
			label: 'Ustawienia',
			template: 'assets/partials/user/settings.html',
			url: 'settings',
		},
		{
			label: 'Upodobania',
			template: 'assets/partials/user/likings.html',
			url: 'likings',
		},
		{
			label: 'Zmiana hasła',
			template: 'assets/partials/user/changePassword.html',
			url: 'changePassword',
		},
	];

	$scope.selectedPage = 0;

	for (var i = 0; i < $scope.pages.length; i++) {
        if ($scope.pages[i].url === $routeParams.page) {
            $scope.selectedPage = i;
            break;
        }
    }

    $scope.onPageSelect = function(page) {
    	$location.search('page', page.url);
    };

});

angular.module('planevent').controller('ProfileInformationsController',
        function($scope, userProfileService, fileUploadService) {

    userProfileService.prepareScope($scope);

    $scope.initAvatarChange = function() {
    	$('#avatar-upload').click();
    };

    $scope.uploadAvatar = function(files) {
    	$scope.uploadingAvatar = true;
        fileUploadService.upload(
                files, '/api/avatar', function(data) {
            $scope.account.avatar = data.path;
            $scope.uploadingAvatar = false;
        });
    };

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

