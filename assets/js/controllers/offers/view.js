'use strict';

angular.module('planevent').controller('OfferListController',
        function($scope, $location, $routeParams, searchService) {

    searchService.resetParams();
    searchService.params.category = $routeParams.categoryId;

    $scope.goToOffer = function(offer) {
        $location.path('/offer/' + offer.id);
    };

    $scope.fetch = function(offset, limit, callback) {
        searchService.fetch(offset, limit, callback);
    };
});

angular.module('planevent').controller('OfferPageController',
        function($scope, $resource, $routeParams, categoriesService) {
    var Offer = $resource('/api/offer/:id');
    $scope.offerDoesNotExists = false;
    $scope.otherError = false;
    var offer = Offer.get({id: $routeParams.offerId},
        function(){
            $scope.fetched = true;
            $scope.offer = offer;
        },
        function(response){
            if (response.status === 404) {
                $scope.offerDoesNotExists = true;
            } else {
                $scope.otherError = true;
            }
        }
    );
    $scope.categories = categoriesService.categories;

    $scope.removeOffer = function() {
        Offer.remove({id: $scope.offer.id});
    };

});

angular.module('planevent').controller('RelatedOffersController',
        function($scope, searchService) {

    $scope.$watch('offer', function() {
        if ($scope.offer === undefined) {
            return;
        }

        var tags_ids = _.map($scope.offer.tags, function(tag) {
            return tag.id;
        });

        searchService.resetParams();
        searchService.categoryEnabled = true;
        searchService.locationEnabled = true;

        searchService.params.location = $scope.offer.address.city;
        searchService.params.category = $scope.offer.category.id;
        searchService.params.exclude_offer_id = $scope.offer.id;
        searchService.params.tags = tags_ids;
        searchService.params.range = 50;

        searchService.fetch(0, 6, function(total_count, offers) {
            $scope.relatedOffers = offers;
        });
    });

});

angular.module('planevent').controller('PromotedOffersController',
        function($scope, offersService) {

    offersService.getPromotedOffers()
    .success(function(promotedOffers) {
        $scope.promotedOffers = promotedOffers;

        var entities = [];
        _.forEach(promotedOffers, function(category) {
            entities = entities.concat(category.offers);
        });
        $scope.entities = entities;
    });
});

angular.module('planevent').controller('RecommendedOffersController',
        function($scope, offersService) {

    offersService.getRecommendations()
    .success(function(recommendations) {
        $scope.recommendations = recommendations;
    });
});
