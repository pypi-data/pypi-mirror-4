function ProcessListCtrl($scope, Process) {
    $scope.processes = Process.query();
}

function ProcessDetailCtrl($scope, $routeParams, $http, Process) {
    $scope.process = Process.get({processId: $routeParams.processId});

    $scope.std = {
        'out': 'not loaded',
        'err': 'not loaded'
    }

    $http.get('/api/process/' + $routeParams.processId + '/stdout').success(function(data) {
        $scope.std.out = data;
    });

    $http.get('/api/process/' + $routeParams.processId + '/stderr').success(function(data) {
        $scope.std.err = data;
    });
}