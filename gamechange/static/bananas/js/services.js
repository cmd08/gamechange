'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('myApp.services', []).
  	service('userService', function(){
	  	return {
	  		getUserinfo: function() {
				Restangular.one('user').get().then(function(response){
			    	console.log(response.data);
			      	return response.data;
			    });
	  		}

	  		// setUserdata: function() {
	  			
	  		// }
	  	}
  	})

.value('version', '0.1');


