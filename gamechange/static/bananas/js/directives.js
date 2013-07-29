'use strict';

/* Directives */


angular.module('myApp.directives', []).
directive('appVersion', ['version', function(version) {
	return function(scope, elm, attrs) {
		elm.text(version);
	};
}]).
directive('backButton', function(){
	return {
		restrict: 'A',

		link: function(scope, element, attrs) {
			element.bind('click', goBack);

			function goBack() {
				history.back();
				scope.$apply();
			}
		}
	}
});
