var FileManagerApp = angular.module('FileManagerApp').config(['fileManagerConfigProvider', function (config) {
    var defaults = config.$get();
    config.set({
        appName: '{{ lab }} storages',
        listUrl: '/' + lab_pk + '/filemanager/list/',
        createFolderUrl: '/' + lab_pk + '/filemanager/createfolder/',
        renameUrl: '/' + lab_pk + '/filemanager/rename/',
        removeUrl: '/' + lab_pk + '/filemanager/remove/',
        uploadUrl: '/' + lab_pk + '/filemanager/upload/',
        downloadFileUrl: '/' + lab_pk + '/filemanager/download/',
        allowedActions: angular.extend(defaults.allowedActions, {
            remove: true,
            changePermissions: false,
            edit: false,
            compress: false,
            compressChooseName: false,
            extract: false
        })
    });
}]);


var app = angular.module('LabrepoApp', ['FileManagerApp', 'unitControllers', 'UnitLinkCtrl', 'unitServices', 'unitLinkServices', 'ui.select2']);
//app.config(function($interpolateProvider) {
//    $interpolateProvider.startSymbol('{[{');
//    $interpolateProvider.endSymbol('}]}');
//
//});