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
        function($scope, $resource, $routeParams, $mdDialog, categoriesService) {

    var Offer = $resource('/api/offer/:offerId', {offerId: '@id'});

    $scope.state = 'viewing';
    $scope.offerDoesNotExists = false;
    $scope.otherError = false;
    $scope.offer = Offer.get({offerId: $routeParams.offerId},
        function(){
            $scope.fetched = true;
            if ($scope.offer.contacts === undefined) {
                $scope.offer.contacts = [];
            }
        },
        function(response){
            if (response.status === 404) {
                $scope.offerDoesNotExists = true;
            } else {
                $scope.otherError = true;
            }
        }
    );
    categoriesService.getCategories(function(categories) {
        $scope.categories = categories;
    });

    $scope.saveOffer = function() {
        $scope.state = 'saving';
        $scope.offer.$save(
            function() {
                $scope.state = 'saved';
            },
            function() {
                $scope.state = 'error';
            }
        );
    };

    $scope.getCategoryName = function(categoryId) {
        var category = categoriesService.getCategoryById(categoryId);
        if (category !== null) {
            return category.name;
        }
    };

    $scope.removeOffer = function() {
        Offer.remove({id: $scope.offer.id});
    };

    $scope.showGallery = function() {
        $mdDialog.show({
            templateUrl: 'assets/partials/offer/galleryModal.html',
            controller: 'GalleryModalController',
            locals: {
                gallery: $scope.offer.gallery,
                editing: $scope.state === 'editing',
            },
        });
    };

    $scope.showEditable = function(form) {
        if ($scope.state === 'editing') {
            form.$show();
        }
    };
});

angular.module('planevent').controller('RelatedOffersController',
        function($scope, searchService) {

    $scope.offer.$promise.then(function() {
        if ($scope.offer === undefined) {
            return;
        }

        var tags_ids = _.map($scope.offer.tags, function(tag) {
            return tag.id;
        });

        searchService.params = {
            location: $scope.offer.address.city,
            category: $scope.offer.category.id,
            exclude_offer_id: $scope.offer.id,
            tags: tags_ids,
            range: 50
        };

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

angular.module('planevent').controller('GalleryModalController',
        function($scope, $mdDialog, gallery, editing) {

    $scope.close = $mdDialog.hide;

    $scope.gallery = gallery;
    $scope.editing = editing;
});
