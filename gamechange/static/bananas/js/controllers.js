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

  Restangular.all('shop').getList().then(function (results) {
    $scope.shop = results.items;
    //console.log($scope.shop );
  });

  $scope.buy = function(cost) {
    if ($scope.user.bananas >= cost)
    {
      $scope.user.bananas -= cost;
      //console.log(cost, ' bananas spent');

      //Update backend through API

    }
    else
    {
      console.log('Not enough bananas');
    }

  };

}

function user_ctrl($scope, Restangular)
{

  Restangular.all('user').customPOST('login', {}, {}, {username: "Ashley", password: "yoMumma"}).then(function (results) {
    $scope.user = results.data;
    //console.log($scope.user);
  });


  //Get back the username and the no of bananas
  // Restangular.all('user').getList().then(function (results) {
  //   $scope.user = results;
  //   console.log($scope.user.username);
  //   console.log($scope.user.bananas);
  // });

  // $scope.spend_bananas = function( cost ) {
  //   if $scope.user.bananas > cost :
  //     $scope.user.bananas -= cost;
  //     return 'valid';
  //   else
  //     return 'invalid';
  // }

}

function popup_ctrl($scope)
{
  
}

 