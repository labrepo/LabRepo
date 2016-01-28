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


var tagServices = angular.module('tagServices', ['ngResource']);
tagServices.factory('Tag', ['$resource',
    function($resource){
        return $resource('/:labId/tags/api/:tagId/', {}, {
            'create': {method:'POST'},
            'delete': {method:'DELETE'},
            'update': {method:'PUT'},
            'query':  {method:'GET', isArray:true},
        });
    }]);

var measurementServices = angular.module('measurementServices', ['ngResource']);
measurementServices.factory('Measurement', ['$resource',
    function($resource){
        return $resource('/:labId/measurements/api/:measurementId/', {}, {
            'get':    {method:'GET'},
            'update': {method:'PUT'}
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
            var message = JSON.parse(message.data);
            if (message.action == 'create') {
                $rootScope.$emit('create_chat_message', message.comment);
            }
            if (message.action == 'update') {
                $rootScope.$emit('update_chat_message', message.comment);
            }
            if (message.action == 'delete') {
                $rootScope.$emit('delete_chat_message', message.comment);
            }
        });

        var methods = {
            get: function() {
                dataStream.send(JSON.stringify({ action: 'get' }));
            }
        };
        return methods;
    }])