'use strict';

angular.module('planevent').controller('OfferAddEditController',
    function($scope, $resource, $routeParams, $location, $upload,
             globalsService) {

        $scope.locationComplete = false;
        $scope.validatingLocation = false;
        $scope.categories = globalsService.categories;
        $scope.contactTypes = globalsService.contactTypes;
        $scope.offerView = 'assets/partials/offerView.html';

        if ($routeParams.offerId === undefined) {
            $scope.offer = {gallery: [], address: {}};
        } else {
            var Offer = $resource('/api/offer/:id');
            $scope.offer = Offer.get({id: $routeParams.offerId}, function() {
                var address = $scope.offer.address;
                $scope.locationComplete = address.city && address.street;
            });
        }

        $scope.goTo = function(section) {
            $scope.step = section;
            $scope.section = 'assets/partials/offerAddEdit/' +
                section + '.html';
        };

        $scope.submit = function() {
            var Offers = $resource('/api/offers');
            var offer = Offers.save($scope.offer , function() {
                $location.path('/offer/' + offer.id);
            });
        };

        $scope.addContact = function() {
            var contacts = $scope.offer.contacts;
            if (contacts === undefined) {
                contacts = $scope.offer.contacts = [];
            }
            contacts[contacts.length] = {};
        };

        $scope.removeContact = function(contactNo) {
            $scope.offer.contacts.splice(contactNo, 1);
        };

        $scope.addTag = function() {
            var tags = $scope.offer.tags;
            if (tags === undefined) {
                tags = $scope.offer.tags = [];
            }
            tags[tags.length] = {};
        };

        $scope.removeTag = function(tagNo) {
            $scope.offer.tags.splice(tagNo, 1);
        };

        $scope.uploadLogo = function(files) {
            uploadImages(files, '/api/image', function(data) {
                $scope.offer.logo = {path: data.path};
            });
        };

        $scope.uploadGallery = function(files) {
            uploadImages(files, '/api/gallery', function(data) {
                var gallery = $scope.offer.gallery;
                gallery[gallery.length] = {path: data.path};
            });
        };

        function uploadImages(files, api, callback) {
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                $scope.upload = $upload.upload({
                    url: api,
                    method: 'POST',
                    file: file,
                // }).progress(function(evt) {
                    // console.log('percent: ' + parseInt(100.0 *
                                   //evt.loaded / evt.total));
                }).success(callback);
                //.error(...)
                //.then(success, error, progress);
            }
        }

        $scope.goTo('info');
    }
);