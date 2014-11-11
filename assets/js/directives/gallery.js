'use strict';

angular.module('planevent').directive('gallery', function(fileUploadService) {
    return {
        restrict: 'EA',
        require: '^ngModel',
        templateUrl: 'assets/partials/directives/gallery.html',
        link: function($scope, element, attrs) {
            function init() {
                var gallery = $scope.$eval(attrs.ngModel);
                $scope.originalGallery = gallery;
                $scope.gallery = gallery;
                $scope.editing = $scope.$eval(attrs.editing);

                $scope._Index = 0;

                $scope.isActive = function(index) {
                    return $scope._Index === index;
                };

                $scope.showPrev = function() {
                    $scope._Index =
                    ($scope._Index > 0) ? --$scope._Index :
                    $scope.gallery.length - 1;
                };

                $scope.showNext = function() {
                    $scope._Index =
                    ($scope._Index < $scope.gallery.length - 1) ?
                    ++$scope._Index : 0;
                };

                $scope.showPhoto = function(index) {
                    $scope._Index = index;
                };

                $scope.removeImage = function(image) {
                    var index = gallery.indexOf(image);
                    if (index > -1) {
                        gallery.splice(index, 1);
                    }
                    $scope.gallery = gallery.slice(0);
                };

                $scope.initImageUpload = function() {
                    $('#add-image-button').click();
                };

                $scope.addImage = function(files) {
                    fileUploadService.upload(
                            files, '/api/gallery', function(data) {
                        gallery[gallery.length] = data;
                        $scope.gallery = gallery.slice(0);
                    });
                };
            }

            $scope.$watchCollection('offer', init);
        }
    };
});

angular.module('planevent').directive('galleryPreview', function() {
    return {
        restrict: 'EA',
        require: '^ngModel',
        templateUrl: 'assets/partials/directives/galleryPreview.html',
        link: function($scope, element, attrs) {
            function init() {
                $scope.gallery = $scope.$eval(attrs.ngModel);
            }
            $scope.limit = parseInt(attrs.limit);
            $scope.$watchCollection('offer', init);
        }
    };
});
