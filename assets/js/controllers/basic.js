'use strict';

angular.module('planevent').controller('HomePageController',
    function($scope, authService) {
        $scope.registrationLandingPage =
            'assets/partials/registrationLandingPage.html';
        $scope.promotedView = 'assets/partials/promotedView.html';
        $scope.recomendationsView = 'assets/partials/recomendationsView.html';

        authService.getLoggedUser(function(loggedUser) {
            $scope.loggedUser = loggedUser;
        });

        $scope.$on('loggedIn', function(event, account) {
            $scope.loggedUser = account;
        });

        $scope.$on('loggedOut', function(event) {
            $scope.loggedUser = null;
        });
    }
);

angular.module('planevent').controller('MainPageController',
    function($scope, categoriesService, searchService) {
        $scope.mainView = 'assets/partials/mainView.html';
        $scope.categoriesView = 'assets/partials/categoriesView.html';
        $scope.offerView = 'assets/partials/offerView.html';
        $scope.searchForm = 'assets/partials/search.html';
        $scope.loggedUserView = 'assets/partials/loggedUser.html';
        $scope.promotedOffersView = 'assets/partials/promotedOffers.html';

        $scope.categories = categoriesService.categories;

        $scope.getPromotedOffers = function() {
            searchService.resetParams();
            searchService.params.category = $routeParams.categoryId;
            searchService.fetch(offset, limit, callback);
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
