var shirkaModule = angular.module('shirka', ['processServices', 'ngCookies']);

shirkaModule.config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
    $routeProvider
        .when('/process', {templateUrl: 'shirka/partials/process-list.html', controller: ProcessListCtrl})
        .when('/process/:processId', {templateUrl: 'shirka/partials/process-detail.html', controller: ProcessDetailCtrl})

        .otherwise({redirectTo: '/process'})
    ;
}]);