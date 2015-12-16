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