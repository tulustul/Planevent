'use strict';

angular.module('planevent').controller('HomePageController',
    function($scope, authService) {
        authService.getLoggedUser(function(loggedUser) {
            $scope.loggedUser = loggedUser;
            $scope.address = $scope.loggedUser.settings.address;
        });

        $scope.$on('loggedIn', function(event, account) {
            $scope.loggedUser = account;
            $scope.address = $scope.loggedUser.settings.address;
        });

        $scope.$on('loggedOut', function(event) {
            $scope.loggedUser = null;
        });
    }
);

angular.module('planevent').controller('MainPageController',
    function($scope, $modal, categoriesService, searchService) {
        $scope.categories = categoriesService.categories;

        // $scope.getPromotedOffers = function() {
        //     searchService.resetParams();
        //     searchService.params.category = $routeParams.categoryId;
        //     searchService.fetch(offset, limit, callback);
        // };

        $scope.$on('showRegistrationForm', function() {
            $scope.showRegistrationForm();
        });

        $scope.showRegistrationForm = function() {
            var registrationScope = $scope.$new(true);
            registrationScope.modal = $modal.open({
                templateUrl: 'assets/partials/auth/registrationModal.html',
                scope: registrationScope,
                windowClass: 'registrationModal',
                controller: 'RegistrationController',
            });
        };

        $scope.showLoginForm = function() {
            var loginScope = $scope.$new(true);
            loginScope.modal = $modal.open({
                templateUrl: 'assets/partials/auth/loginModal.html',
                scope: loginScope,
                windowClass: 'loginModal',
                controller: 'LoginController',
            });
        };
    }
);

angular.module('planevent').controller('CategoriesController',
    function($scope, $location, $routeParams) {
        var categoryId = parseInt($routeParams.categoryId);
        for (var i in $scope.categories) {
            var category = $scope.categories[i];
            if (category.id === categoryId) {
                $scope.selectedCategory = category;
                break;
            }
        }

        $scope.searchCategory = function(category) {
            if (category !== undefined) {
                $scope.selectedCategory = category;
            }
            $location.path('/offers/' + $scope.selectedCategory.id);
        };
    }
);

angular.module('planevent').controller('FeedbackController',
        function($scope, $http, authService) {

    $scope.title = '';
    $scope.content = '';

    $scope.sendFeedback = function() {
        var userEmail = '';
        if (authService.loggedUser !== null) {
            userEmail = authService.loggedUser.email;
        }

        if ($scope.title === '') {
            $scope.status = 'empty';
            return;
        }

        $scope.status = 'waiting';

        $http.put('/api/feedbacks', {
            title: $scope.title,
            content: $scope.content,
            email: userEmail
        })
        .success(function() {
            $scope.status = 'success';
            $scope.title = '';
            $scope.content = '';
        })
        .error(function() {
            $scope.status = 'error';

        });
    };
});
