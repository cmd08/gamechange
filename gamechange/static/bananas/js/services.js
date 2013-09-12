'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('myApp.services', [])
  	// .service('userService', function(){
	  // 	return {
	  // 		getUserinfo: function() {
			// 	Restangular.one('user').get().then(function(response){
			//     	console.log(response.data);
			//       	return response.data;
			//     });
	  // 		}

	  // 		// setUserdata: function() {
	  			
	  // 		// }
	  // 	}
  	// })

	.service('dialogService', ['$dialog', function ($dialog) {

		var dialogDefaults = {
		    backdrop: true,
		    keyboard: true,
		    backdropClick: false,
		    dialogFade: true,
		    templateUrl: '/static/bananas/partials/dialog.html'
		};

		var dialogOpts = {
		    closeText: 'Close',
		    actionText: 'OK',
		    header: 'Proceed?',
		    body: 'Perform this action?'
		};

		this.showDialog = function (customDialogDefaults, customDialogOpts) {
		    //Create temp objects to work with so that we dont affect other callers
		    var tempDialogDefaults = {};
		    var tempDialogOpts = {};

		    //Copy custom parameters to default parameters in this service
		    angular.extend(tempDialogDefaults, dialogDefaults, customDialogDefaults);

		    //Copy custom options to default options in this service 
		    angular.extend(tempDialogOpts, dialogOpts, customDialogOpts);

		    if (!tempDialogDefaults.controller) {
		        tempDialogDefaults.controller = function ($scope, dialog) {
		            $scope.dialogOpts = tempDialogOpts;
		            $scope.dialogOpts.close = function (result) {
		                dialog.close(result);
		            };
		            $scope.dialogOpts.callback = function () {
		                dialog.close();
		                customDialogOpts.callback();
		            };
		        }
		    }

		    var d = $dialog.dialog(tempDialogDefaults);
		    d.open();
		};

		this.showMessage = function (title, message, buttons) {
		    var defaultButtons = [{result:'ok', label: 'OK', cssClass: 'btn-primary'}];
		    var msgBox = new $dialog.dialog({
		        dialogFade: true,
		        templateUrl: 'template/dialog/message.html',
		        controller: 'MessageBoxController',
		        resolve: {
                    model: function () {
                        return {
                            title: title,
                            message: message,
                            buttons: buttons == null ? defaultButtons : buttons
                        };
                    }
                }
		    });
		    return msgBox.open();
		};

	}])

.value('version', '0.1');



