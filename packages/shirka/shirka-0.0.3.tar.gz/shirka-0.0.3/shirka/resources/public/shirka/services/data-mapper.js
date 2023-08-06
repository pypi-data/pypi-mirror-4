var processServices = angular.module('processServices', ['ngResource']);

processServices.factory('Process', function($resource) {
    return $resource('/api/process/:processId', {}, {
        get:    {method: 'GET', params:{processId: 'processId'}},
        query:  {method: 'GET', isArray: false},
        update: {method: 'PUT', params:{processId: '@id'}}
    });
});