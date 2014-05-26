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
        function($scope, $resource, $routeParams, globalsService) {
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
    $scope.categories = globalsService.categories;

    $scope.removeOffer = function() {
        Offer.remove({id: $scope.offer.id});
    };

});

angular.module('planevent').controller('RelatedOffersController',
        function($scope, $resource) {

    var OffersSearch = $resource('/api/offers/search');

    $scope.$watch('offer', function() {
        if ($scope.offer === undefined) {
            return;
        }

        var tags_ids = _.map($scope.offer.tags, function(tag) {
            return tag.id;
        });

        var params = {
            category: $scope.offer.category.id,
            exclude_offer_id: $scope.offer.id,
            tags: tags_ids,
            range: 50,
            limit: 5
        };

        params.location = $scope.offer.address.city;

        $scope.relatedOffers = OffersSearch.query(params);
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
