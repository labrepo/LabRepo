var unitControllers = angular.module('unitControllers', []);

unitControllers.controller('UnitDetailCtrl', ['$scope', 'Unit',
    function($scope, Unit) {

        $scope.units = Unit.query({labId: lab_pk})

        $scope.getUnit = function(UnitId) {
            $scope.unit = Unit.get({labId: lab_pk, unitId: UnitId}, function(phone) {});
            $scope.$broadcast('UnitLoaded', {'unitId': UnitId});
        };

        $scope.saveUnit = function() {
            $scope.unit.$save({unitId: $scope.unit.id })
        };

        $scope.getUnitbyId = function(id){
            return  $scope.units.filter(function(v) {
                return v.id === id;
            })[0].sample;
        };

        Unit.prototype.$save = function() {
            if (this.id) {
                return this.$update({unitId: $scope.unit.id,labId: lab_pk  });
            } else {
                return this.$create();
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