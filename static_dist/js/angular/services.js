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

var commentServices = angular.module('commentServices', ['ngResource']);
commentServices.factory('Comment', ['$resource',
    function($resource){
        return $resource('/:labId/comment/api/:instanceType/:instanceId/:commentId/', {}, {
            'create': {method:'POST'},
            'delete': {method:'DELETE'},
            'update': {method:'PUT'},
            'query':  {method:'GET', isArray:true
            },
        });
    }]);

commentServices.config(function($resourceProvider) {
    $resourceProvider.defaults.stripTrailingSlashes = false;
});


var storageServices = angular.module('storageServices', ['ngResource']);
storageServices.factory('Storage', ['$resource',
    function($resource){
        return $resource('/:labId/storages/api/:storageId/', {}, {
            'create': {method:'POST'},
            'delete': {method:'DELETE'},
            'update': {method:'PUT'},
            'query':  {method:'GET', isArray:true
            },
        });
    }]);

commentServices.config(function($resourceProvider) {
    $resourceProvider.defaults.stripTrailingSlashes = false;
});


var chatSocketServices = angular.module('chatSocketServices', ['ngWebSocket']);
chatSocketServices.factory('chatMessage', ['$websocket', '$rootScope',
    function($websocket, $rootScope) {
        var experiment =  angular.element(document.querySelector('#experiment_row')).data('experiment-pk');

        var dataStream = $websocket('ws://'+ LabRepo.domain + '/chat/'  + experiment + '/');

        dataStream.onMessage(function(message) {
            $rootScope.$emit('new_chat_message', JSON.parse(message.data).comment);
        });

        var methods = {
            get: function() {
                dataStream.send(JSON.stringify({ action: 'get' }));
            }
        };
        return methods;
    }])