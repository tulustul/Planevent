'use strict';

angular.module('planevent').factory('httpErrorHandler',
        function($q, $rootScope) {
    return {
        response: function (response) {
            return response || $q.when(response);
        },
        responseError: function (rejection) {
            if (rejection.status === 401) {
                $rootScope.$broadcast('unauthorized');
            } else if (rejection.status === 403) {
                $rootScope.$broadcast('forbidden');
            } else if (rejection.status === 0) {
                $rootScope.$broadcast('connectionError');
            }
            return $q.reject(rejection);
            }
        };
    }
);

angular.module('planevent').config(function($httpProvider) {
    $httpProvider.interceptors.push('httpErrorHandler');
});

angular.module('planevent').run(function($rootScope, toastService) {

    $rootScope.$on('unauthorized', function() {
        toastService.show('Musisz być zalogowany by wykonać tę akcję');
    })

    $rootScope.$on('forbidden', function() {
        toastService.show('Nie posiadasz odpowiednich uprawnień');
    })

    $rootScope.$on('connectionError', function() {
        toastService.show('Błąd połączenia. Sprawdź łączę internetowe.');
    })
});
