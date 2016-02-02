angular.module('LabrepoApp')
    .directive('commentsScroll', ['$timeout', function ($timeout) {
        return {
            restrict: 'A',
            link: function (scope, element, attr) {
                if (scope.$last === true) {
                    $timeout(function () {
                        var $comments = $(element).parent()
                        $comments.css('max-height', window.innerHeight -430)
                        var sidebar_height = $('.main-sidebar').height();
                        if (window.innerHeight > 650) {
                            $comments.css('max-height', sidebar_height - 325).css('min-height', sidebar_height - 325);
                        }
                        $comments.scrollTop($comments[0].scrollHeight);

                    });
                }
            }
        }
    }])
    .directive('ngReallyClick', [function() {
        return {
            restrict: 'A',
            link: function(scope, element, attrs) {
                element.bind('click', function() {
                    var message = attrs.ngReallyMessage;
                    if (message && confirm(message)) {
                        scope.$apply(attrs.ngReallyClick);
                    }
                });
            }
        }
    }]);
