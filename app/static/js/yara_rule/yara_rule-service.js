'use strict';

angular.module('ThreatKB')
    .factory('Yara_rule', ['$resource', function ($resource) {
        return $resource('ThreatKB/yara_rules/:id', {}, {
            'query': {method: 'GET', isArray: true},
            'get': {method: 'GET'},
            'update': {method: 'PUT'}
        });
    }]);

angular.module('ThreatKB')
    .factory('Yara_ruleExport', ['$q', '$timeout', '$http',
        function ($q, $timeout, $http) {

            return ({export: export_signatures});

            function export_signatures() {
                return $http.get('/ThreatKB/yara_rules', {}).then(function (data) {

                }, function (error) {
                    return $q.reject(error.data);
                })
            };

        }]);
