var unitServices = angular.module('unitServices', ['ngResource']);
unitServices.factory('Unit', ['$resource',
    function($resource){
        return $resource('/:labId/units/api/unit/:unitId', {}, {
            'update': {method:'PUT' },
            'create': {method:'POST' },
            'query':  {method:'GET', isArray:true},
        });
    }]);

var unitLinkServices = angular.module('unitLinkServices', ['ngResource']);
unitLinkServices.factory('UnitLink', ['$resource',
    function($resource){
        return $resource('/:labId/units/api/unit-links/:linkId/', {}, {
            'create': {method:'POST'},
            'delete': {method:'DELETE' },
            'query':  {
                method:'GET',
                url: '/:labId/units/api/unit-links/list/:unitId/',
                params:{labId: '@labId', unitId: '@unitId'},
                isArray:true
            },
        });
    }]);

unitLinkServices.config(function($resourceProvider) {
    $resourceProvider.defaults.stripTrailingSlashes = false;
});
