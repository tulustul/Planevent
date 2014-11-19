'use strict';

angular.module('planevent').controller('OfferListController',
        function($scope, $location, $routeParams, searchService) {

    searchService.resetParams();
    searchService.params.category = $routeParams.categoryId;

    $scope.goToOffer = function(offer) {
        $location.path('/offers/' + offer.id);
    };

    $scope.fetch = function(offset, limit, callback) {
        searchService.fetch(offset, limit, callback);
    };
});

angular.module('planevent').controller('OfferPageController',
        function($scope, $http, $resource, $routeParams, $mdDialog,
                 toastService, $location, categoriesService,
                 fileUploadService) {

    var Offer = $resource('/api/offers/:offerId', {offerId: '@id'}),
        offerId = $routeParams.offerId;

    $scope.state = 'viewing';
    $scope.error = '';

    function fetchOffer() {
        $scope.offer = Offer.get({offerId: $routeParams.offerId},
            function(){
                $scope.fetched = true;
                if ($scope.offer.contacts === undefined) {
                    $scope.offer.contacts = [];
                }
                if ($scope.offer.gallery === undefined) {
                    $scope.offer.gallery = [];
                }
            },
            function(response){
                if (response.status === 404) {
                    $scope.error = 'offerDoesNotExist';
                } else {
                    $scope.error = 'unknown';
                }
            }
        );

    }

    if (offerId === 'new') {
        $scope.offer = new Offer({
            gallery: [],
            contacts: [],
        });
        $scope.fetched = true;
    } else {
        fetchOffer();
    }

    categoriesService.getCategories(function(categories) {
        $scope.categories = categories;
    });

    $scope.saveOffer = function() {
        $scope.state = 'saving';
        $scope.offer.$save(
            function(offer) {
                toastService.show('Zmiany zapisane');
                $scope.state = 'viewing';
                $scope.offer = offer;
                $location.path('/offers/' + offer.id);
            },
            function() {
                $scope.state = 'viewing';
                toastService.show('Nie można zapisać zmian');
            }
        );
    };

    $scope.cancelEditing = function() {
        fetchOffer();
    };

    $scope.getCategoryName = function(categoryId) {
        var category = categoriesService.getCategoryById(categoryId);
        if (category !== null) {
            return category.name;
        }
    };

    $scope.removeOffer = function() {
        $mdDialog.show({
            templateUrl: 'assets/partials/offer/removeModal.html',
            controller: 'RemoveOfferModalController',
        }).then(function() {
            $scope.state = 'saving';
            $http.post('/api/offer/' + $scope.offer.id + '/delete')
            .success(function(response) {
                $scope.offer.status = response.status;
                toastService.show('Usunięto kategorię');
                $location.path('/');
            })
            .error(function(response, status_code) {
                if (status_code === 403) {
                    toastService.show(
                        'Nie posiadasz uprawnień do usunięcia tej oferty'
                    );
                } else {
                    toastService.show(
                        'Nie można usunąć oferty - nieznany błąd'
                    );
                }
                $scope.state = 'viewing';
            });
        });

    };

    $scope.activateOffer = function() {
        $scope.state = 'saving';
        $http.post('/api/offer/' + $scope.offer.id + '/activate')
        .success(function(response) {
            $scope.offer.status = response.status;
            $scope.state = 'viewing';
            toastService.show('Aktywowano ofertę');
        });
    };

    $scope.deactivateOffer = function() {
        $scope.state = 'saving';
        $http.post('/api/offer/' + $scope.offer.id + '/deactivate')
        .success(function(response) {
            $scope.offer.status = response.status;
            $scope.state = 'viewing';
            toastService.show('Deaktywowano ofertę');
        });
    };

    $scope.setState = function(state) {
        $scope.state = state;
    };

    $scope.initPreviewImageUpload = function() {
        $('#upload-logo').click();
    };

    $scope.uploadPreviewImage = function(files) {
        fileUploadService.upload(
                files, '/api/logo', function(data) {
            $scope.offer.preview_image_url = data.path;
        });
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

    $scope.cancel = $mdDialog.cancel;

    $scope.gallery = gallery;
    $scope.editing = editing;
});

angular.module('planevent').controller('RemoveOfferModalController',
        function($scope, $mdDialog) {

    $scope.cancel = $mdDialog.cancel;
    $scope.hide = $mdDialog.hide;

});