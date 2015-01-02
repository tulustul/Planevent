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
        toastService.warn('Musisz być zalogowany by wykonać tę akcję');
        $rootScope.$broadcast('loggedOut');
    })

    $rootScope.$on('forbidden', function() {
        toastService.warn('Nie posiadasz odpowiednich uprawnień');
    })

    $rootScope.$on('connectionError', function() {
        toastService.error('Błąd połączenia. Sprawdź łączę internetowe.');
    })
});
