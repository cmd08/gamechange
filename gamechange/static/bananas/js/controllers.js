'use strict';

/* Controllers */

angular.module('myApp.controllers', []).
controller('MyCtrl1', [function() {

}])
.controller('MyCtrl2', [function() {

}])
.controller('MyCtrl3', [function() {

}])
.controller('MyCtrl4', [function() {

}]);

function shop_products_ctrl($scope, Restangular)
{
  	// $scope.shop = [
  	// 	{name:'Water', cost:2, description:'water, what more can I say!!!'},
  	// 	{name:'Coconut', cost:5, description:'Green or brown, who knows??'},
  	// 	{name:'Mango', cost:10, description:'water, what more can I say!!!'}
  	// ];

  $scope.shop = Restangular.all("shop").getList();


}

