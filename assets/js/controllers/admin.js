'use strict';

angular.module('planevent').controller('DatabaseManagementController',
        function($scope, $http, $timeout) {

    function countProgress(progressCounter) {
        $scope.taskState = 'Working';
        (function progress() {
            $http.get('api/task/' + progressCounter + '/progress')
                .success(function(response) {
                    $scope.task = response;
                    $scope.task.percentage =
                        ((response.progress / response.max) * 100)
                         .toFixed(1);

                    if ($scope.isWorking($scope.task)) {
                        $timeout(progress, 1000);
                    }
                });
        })();
    }

    $scope.migrations = {
        'import': {
            name: 'import',
            exec: function(spreadsheetName, worksheetName) {
                $scope.resetMessages();

                $http.post('/api/database/migration', {
                    spreadsheet: spreadsheetName,
                    worksheet: worksheetName,
                })
                .success(function(response) {
                    $scope.addSuccess(response.message);
                    countProgress(response.progress_counter);
                })
                .error(function(msg) {
                    $scope.addDanger(msg);
                });
            }
        },
        'export': {
            name: 'export',
            exec: function() {
                $scope.resetMessages();

                $http.get('/api/database/migration')
                .success(function(response) {
                    $scope.addSuccess(response.message);
                    countProgress(response.progress_counter);
                })
                .error(function(msg) {
                    $scope.addDanger(msg);
                });
            }
        }
    };

    $scope.isWorking = function(task) {
        if (task === undefined || task === null) {
            return false;
        }
        return task.status === 'PENDING' || task.status === 'WORKING';
    };

    $scope.cancelTask = function(task) {
        $scope.resetMessages();
        $http.post('/api/task/' + task.id + '/cancel')
            .success(function(msg) {
                    $scope.addSuccess(msg);
                })
            .error(function(msg) {
                    $scope.addDanger(msg);
                }
            );
    };

    $scope.updateSchema = function() {
        $scope.resetMessages();
        $http.post('/api/database/update')
            .success(function(msg) {
                    $scope.addSuccess(msg);
                })
            .error(function(msg) {
                    $scope.addDanger(msg);
                }
            );
    };

    $scope.clearDatabase = function() {
        $scope.resetMessages();
        $http.post('/api/database/clear')
            .success(function(msg) {
                    $scope.addSuccess(msg);
                })
            .error(function(msg) {
                    $scope.addDanger(msg);
                }
            );
    };

    $scope.generateRandomData = function(quantity) {
        var iquantity = parseInt(quantity);

        $scope.resetMessages();

        if (isNaN(iquantity)) {
            $scope.addDanger('Incorrect quantity: ' + quantity);
            return;
        }

        $http.post('/api/database/generate', iquantity)
            .success(function(response) {
                $scope.addSuccess(response.message);
                countProgress(response.progress_counter);
            })
            .error(function(msg) {
                $scope.addDanger(msg);
            });
    };
});

angular.module('planevent').controller('AdminPageController',
        function($scope, $resource) {

    $scope.offerPromotionView = 'assets/partials/admin/offerPromotion.html';
    $scope.categoriesView = 'assets/partials/admin/categories.html';
    $scope.subcategoriesView = 'assets/partials/admin/subcategories.html';
    $scope.statisticsView = 'assets/partials/admin/statistics.html';
    $scope.abTestsView = 'assets/partials/admin/abtests.html';
    $scope.databaseView = 'assets/partials/admin/database.html';
    $scope.feedbacksView = 'assets/partials/admin/feedbacks.html';

    var Offer = $resource('/api/offer/:id');
    var OfferPromotion = $resource('/api/offer/:id/promotion/:promotion',
        {id:'@id', promotion: '@promotion'}
    );

    $scope.offer = undefined;
    $scope.saved = false;
    $scope.offerDoesNotExists = false;
    $scope.unknownError = false;


    $scope.resetMessages = function() {
        $scope.dangers = [];
        $scope.warnings = [];
        $scope.successes = [];

    };
    $scope.resetMessages();

    $scope.addDanger = function(msg) {
        $scope.dangers[$scope.dangers.length] = msg;
    };

    $scope.addWarning = function(msg) {
        $scope.warnings[$scope.warnings.length] = msg;
    };

    $scope.addSuccess = function(msg) {
        $scope.successes[$scope.successes.length] = msg;
    };

    $scope.getOffer = function(offerId) {
        $scope.resetMessages();

        $scope.offer = undefined;
        $scope.saved = false;
        $scope.unknownError = false;

        if (offerId === '') {
            return;
        }

        $scope.offer = Offer.get({id: offerId},
            function(){},
            function(response){
                $scope.offer = undefined;
                if (response.status === 404) {
                    $scope.addDanger('Offer does not exists!');
                } else {
                    $scope.addDanger('Unknown error');
                }
            }
        );
    };

    $scope.savePromotion = function(offerId) {
        $scope.resetMessages();

        if ($scope.offer === undefined) {
            return;
        }
        OfferPromotion.save({
                id: offerId,
                promotion: $scope.offer.promotion
            },
            function(){
                $scope.saved = true;
                $scope.addSuccess('Offer saved');
            },
            function(response){
                if (response.status === 404) {
                    $scope.addDanger('Offer does not exists!');
                } else {
                    $scope.addDanger('Unknown error');
                }
            }
        );
    };
});

angular.module('planevent').controller('AdminFeedbacksController',
        function($scope, $http) {
    var LIMIT = 10;

    $scope.getFeedbacks = function(checked, offset) {
        $scope.checked = checked;

        $http.get('/api/feedbacks', {params: {
            checked: checked,
            limit: LIMIT,
            offset: offset
        }})
        .success(function(response){
            var pages = response.pages, i;

            $scope.feedbacks = response.feedbacks;
            $scope.page = response.page;

            $scope.pages = [];
            for (i = 0; i < pages; i++) {
                $scope.pages.push(i);
            }
        })
        .error(function() {
            $scope.addDanger('Unknown error while fetching feedbacks');
        });
    };

    $scope.goToPage = function(page) {
        $scope.getFeedbacks($scope.checked, (page) * LIMIT);
    };

    $scope.markAsChecked = function(feedback) {
        $http.post('/api/feedback/' + feedback.id + '/check')
        .success(function() {
            feedback.checked = true;
        });
    };
});
