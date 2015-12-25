var unitControllers = angular.module('unitControllers', []);

unitControllers.controller('UnitDetailCtrl', ['$scope', 'Unit',
    function($scope, Unit) {
        $scope.experiment_id =  angular.element(document.querySelector('#experiment_row')).data('experiment-pk');
//        $scope.units = Unit.query({labId: lab_pk, experiment_pk: experiment_id})
        $scope.units = Unit.query({labId: lab_pk})

        $scope.getUnit = function(UnitId) {
            $scope.unit = Unit.get({labId: lab_pk, unitId: UnitId}, function(phone) {});
            $scope.$broadcast('UnitLoaded', {'unitId': UnitId});
        };

        $scope.createUnit = function() {
            Unit.create(
                {labId: lab_pk},
                {
                    lab: lab_pk,
                    sample:'New Unit #',
                    experiments: [exp_pk,]
                },
                function(unit){
                    $scope.$broadcast('UnitLoaded', {'unitId': unit.id});
                    graph.addNode({
                        id: unit.id,
                        index: 0,
                        link: "#",
                        score: 2,
                        size: 1,
                        text: unit.sample,
                        type: "circle",
                        weight: 1,
                    });
                    $scope.unit = unit
                });
        };

        $scope.addUnit = function() {
            for (i in $scope.added_units){
                var unit = $scope.getUnitbyId($scope.added_units[i]);
                unit.experiments.push($scope.experiment_id);
                $scope.units.push(unit);
                Unit.update({unitId: unit.id,labId: lab_pk}, unit, function(unit){
                    graph.addNode({
                        id: unit.id,
                        index: 0,
                        link: "#",
                        score: 2,
                        size: 1,
                        text: unit.sample,
                        type: "circle",
                        weight: 1,
                    });
                    angular.element(document.querySelector('#add_unit')).modal('toggle');
                    $scope.added_units = null;
                })
            }
        };

        $scope.saveUnit = function() {
            Unit.update({unitId: $scope.unit.id,labId: lab_pk}, $scope.unit, function(unit){
                graph.updateNodeText(unit.id, unit.sample)
                graph.updateParents(unit.id, unit.parent)
            })
//            $scope.unit.$save({unitId: $scope.unit.id })
        };

        $scope.getUnitbyId = function(id){
            return  $scope.units.filter(function(v) {
                return v.id == id;
            })[0];
        };

        Unit.prototype.$save = function() {
            if (this.id) {
                return this.$update({unitId: $scope.unit.id,labId: lab_pk});
            } else {
                return this.$create({labId: lab_pk});
            }
        };
    }]);

var UnitLinkCtrl = angular.module('UnitLinkCtrl', []);
UnitLinkCtrl.controller('UnitLinkCtrl', ['$scope', 'UnitLink',
    function($scope, UnitLink) {
//        $scope.unitLinks = UnitLink.query({labId: lab_pk, unitId: $scope.$parent.unit})

        $scope.$on('UnitLoaded', function(e, unitId) {
            $scope.getUnitLinks(unitId.unitId)
        });

        $scope.getUnitLinks = function(unitId) {
            $scope.unitLinks = UnitLink.query({labId: lab_pk, unitId: unitId})
        };

        $scope.createUnitLink = function() {
            var link = UnitLink.create({labId: lab_pk}, {link:$scope.link, parent: $scope.unit.id})
            $scope.unitLinks.push(link);
            $scope.link = null;
        };

        $scope.deleteUnitLink = function(UnitLinkId, index) {
            UnitLink.delete({labId: lab_pk, linkId: UnitLinkId})
            $scope.unitLinks.splice(index,1);
        };

    }]);

var chatCtrl = angular.module('chatCtrl', []);

chatCtrl.controller('chatCtrl', ['$scope', '$sce', '$rootScope', 'Comment', 'AuthUser', 'chatMessage',
    function($scope, $sce, $rootScope, Comment, AuthUser, chatMessage) {

        $scope.object_id =  angular.element(document.querySelector('#experiment_row')).data('experiment-pk');
        $scope.comments = angular.extend(Comment.query({labId: lab_pk, instanceType: 'experiment', instanceId: 1}),chatMessage.collection)

        $rootScope.$on('new_chat_message', function(e, comment){
            $scope.comments.push(comment);
        });

        $scope.createComment = function() {
            var comment = Comment.create(
                {labId: lab_pk, instanceType: 'experiment', instanceId: 1},
                {
                    text: $scope.text,
                    instance_type: 'experiment',
                    object_id: $scope.object_id,
                    init_user: AuthUser.id
                })
//            $scope.comments.push(comment);
            $scope.text = null;
        };

        $scope.setComment = function(comment) {
            $scope.comment = comment;
        };

        $scope.updateComment = function() {
            var comment = Comment.create(
                {labId: lab_pk, instanceType: 'experiment', instanceId: 1},
                $scope.comment)
            angular.element(document.querySelector('#comment-modal')).modal('toggle');
        };

        $scope.deleteComment = function() {
            var comment = Comment.delete(
                {labId: lab_pk, instanceType: 'experiment', instanceId: 1, commentId: $scope.comment.id},
                function(){
                    var index = $scope.comments.indexOf(comment);
                    $scope.comments.splice(index, 1);
                }
            )
            angular.element(document.querySelector('#confirm-delete-comment')).modal('toggle');
        };

        $scope.renderHtml = function(html_code)
        {
            return $sce.trustAsHtml(html_code);
        };

        $scope.summernote_config = window.summernote_config;
        $scope.summernote_send = function(e) {
            if ((e.keyCode == 10 || e.keyCode == 13) && (e.ctrlKey || e.shiftKey) && $scope.text)
            {
                e.preventDefault();
                $scope.createComment()
            }
            if ((e.keyCode == 10 || e.keyCode == 13) && (e.ctrlKey || e.shiftKey)) {
                e.preventDefault();
            }
        }

    }]);


var StorageCtrl = angular.module('StorageCtrl', []);
StorageCtrl.controller('StorageCtrl', ['$scope', 'Storage',
    function($scope, Storage) {

        $scope.storages = Storage.query({labId: lab_pk})
        $scope.button_text = 'Create';

        $scope.saveStorage = function() {
            $scope.storage.lab = lab_pk;
            if (!$scope.storage.id){
                Storage.create({labId: lab_pk}, $scope.storage, function(storage) {
                    $scope.storages.push(storage);
                })
            } else{
                var index = $scope.storages.indexOf($scope.storage);
                var storage = Storage.update(
                    {labId: lab_pk, storageId: $scope.storage.id},
                    $scope.storage,
                    function(storage){
                        $scope.storages[index] = storage;
                    }
                )
            }
            $scope.button_text = 'Create';
            $scope.storage = {};
            $scope.storage.type = 1;

            angular.forEach(
                angular.element("input[type='file']"),
                function(inputElem) {
                    angular.element(inputElem).val(null);
                });
        };

        $scope.setStorage = function(storage) {
            $scope.storage = storage;
            $scope.button_text = 'Update';
        };

        $scope.cancelEdit = function() {
            $scope.storage = {};
            $scope.storage.type = 1;
            $scope.button_text = 'Create';
        };

        $scope.deleteStorage = function(storage) {
           Storage.delete(
                {labId: lab_pk, storageId: storage.id},
                function(){
                    var index = $scope.storages.indexOf(storage);
                    $scope.storages.splice(index, 1);
                }
            )
        };
    }]);
