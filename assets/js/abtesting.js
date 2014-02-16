'use strict';

planevent.service('abTestingService', function($resource) {

    this.Experiments = $resource('/api/experiments');
    this.Activate = $resource('/api/experiment/:name/activate');
    this.Deactivate = $resource('/api/experiment/:name/deactivate');

    this.saveABTest = function(abTest, callback) {
        var experiment = this.Experiments.save(abTest,
            function() {
                if (callback !== undefined) {
                    callback(experiment, 200);
                }
            },
            function(response) {
                if (callback !== undefined) {
                    callback(null, response.status, response.data.error);
                }
            }
        );
    };

    this.getExperiments = function(active, callback) {
        // TODO pagination
        var experiments = this.Experiments.query({
            active: active,
            offset: 0,
            limit: 200
        }, function() {
            if (callback !== undefined) {
                callback(experiments);
            }
        });
    };

    this.activate = function(experiment, callback) {
        var message = this.Activate.get({name: experiment.name},
            function() {
                if (callback !== undefined) {
                    callback(message, 200);
                }
            },
            function(response) {
                if (callback !== undefined) {
                    callback(null, response.status, response.data.error);
                }
            }
        );
    };

    this.deactivate = function(experiment, callback) {
        var message = this.Deactivate.get({name: experiment.name},
            function() {
                if (callback !== undefined) {
                    callback(message, 200);
                }
            },
            function(response) {
                if (callback !== undefined) {
                    callback(null, response.status, response.data.error);
                }
            }
        );
    };

});

planevent.controller('ABTestingManagementController',
        function($scope, abTestingService) {

    $scope.activeFilter = null;
    $scope.editedExperiment = null;

    $scope.getExperiments = function(active, skipFormRecovery) {
        if (skipFormRecovery !== true) {
            $('#ab-edition-form').appendTo($('#experiment-edition-temp'));
        }
        abTestingService.getExperiments(active,
                                        function(experiments) {
            $scope.experiments = experiments;
        });
    };

    $scope.createExperiment = function() {
        $scope.experiments[$scope.experiments.length] = {
            name: 'Nowy eksperyment',
            variations: []
        };
    };

    $scope.editExperiment = function(experiment, event) {
        if ($scope.editedExperiment === experiment) {
            $scope.editedExperiment = null;
            $('#ab-edition-form').appendTo($('#experiment-edition-temp'));
        } else {
            $scope.editedExperiment = experiment;
            $('#ab-edition-form-section').hide();
            $('#ab-edition-form').insertAfter($(event.currentTarget));
            $('#ab-edition-form-section').slideDown(100);
        }
    };

    $scope.saveExperiment = function(experiment) {
        $scope.resetMessages();
        abTestingService.saveABTest(experiment,
                                    function(message, status, error) {
            if (status === 200) {
                $scope.addSuccess('Experiment saved.');
            } else {
                $scope.addDanger(error);
            }
        });
    };

    $scope.addVariation = function(experiment) {
        experiment.variations[experiment.variations.length] = {
            name: 'Nowa wariacja',
            probability: 1
        };
    };

    $scope.removeVariation = function(experiment, i) {
        experiment.variations.splice(i ,1);
    };

    $scope.activate = function(experiment) {
        $scope.resetMessages();
        abTestingService.activate(experiment,
                                    function(editedExp, status, error) {
                if (status === 200) {
                    experiment.active = editedExp.active;
                    experiment.in_preparations = editedExp.in_preparations;
                    experiment.started_at = editedExp.started_at;
                    $scope.addSuccess('Experiment activated');
                } else {
                    $scope.addDanger(error);
                }
            }
        );
    };

    $scope.deactivate = function(experiment) {
        $scope.resetMessages();
        abTestingService.deactivate(experiment,
                                    function(editedExp, status, error) {
                if (status === 200) {
                    experiment.active = editedExp.active;
                    experiment.in_preparations = editedExp.in_preparations;
                    experiment.ended_at = editedExp.ended_at;
                    experiment.winner_name = editedExp.winner_name;
                    $scope.addSuccess('Experiment deactivated');
                } else {
                    $scope.addDanger(error);
                }
            }
        );
    };

    $scope.getExperiments(null, true);

});