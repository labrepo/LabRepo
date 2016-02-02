angular.module('LabrepoApp').factory('Unit', ['$resource',
    function($resource){
        return $resource('/:labId/units/api/unit/:unitId', {}, {
            'update': {method:'PUT' },
            'create': {method:'POST' },
            'query':  {method:'GET', isArray:true},
        });
    }]);

angular.module('LabrepoApp').factory('UnitLink', ['$resource',
    function($resource){
        return $resource('/:labId/units/api/:unitId/unit-links/:linkId/', {}, {
            'create': {method:'POST'},
            'delete': {method:'DELETE' },
            'query':  {method:'GET', isArray:true},
        });
    }]);

angular.module('LabrepoApp').factory('Comment', ['$resource',
    function($resource){
        return $resource('/:labId/comment/api/:instanceType/:instanceId/:commentId/', {}, {
            'create': {method:'POST'},
            'delete': {method:'DELETE'},
            'update': {method:'PUT'},
            'query':  {method:'GET', isArray:true
            },
        });
    }]);


angular.module('LabrepoApp').factory('Storage', ['$resource',
    function($resource){
        return $resource('/:labId/storages/api/:storageId/', {}, {
            'create': {method:'POST'},
            'delete': {method:'DELETE'},
            'update': {method:'PUT'},
            'query':  {method:'GET', isArray:true
            },
        });
    }]);


angular.module('LabrepoApp').factory('Tag', ['$resource',
    function($resource){
        return $resource('/:labId/tags/api/:tagId/', {}, {
            'create': {method:'POST'},
            'delete': {method:'DELETE'},
            'update': {method:'PUT'},
            'query':  {method:'GET', isArray:true},
        });
    }]);

angular.module('LabrepoApp').factory('Measurement', ['$resource',
    function($resource){
        return $resource('/:labId/measurements/api/:measurementId/', {}, {
            'get':    {method:'GET'},
            'update': {method:'PUT'}
        });
    }]);


angular.module('LabrepoApp').factory('chatMessage', ['$websocket', '$rootScope',
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