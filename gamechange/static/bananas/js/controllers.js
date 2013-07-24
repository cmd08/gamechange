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

  $scope.buy = function(product) {
    console.log("BUY!")
    Restangular.one('shop', product.id).customPOST('buy').then(function(){
      Restangular.one('user', $scope.user.id).get().then(function(response){
      console.log(response.data);

      $scope.user.bananas = response.data.bananas;
    });
    });


    // if ($scope.user.bananas >= cost)
    // {
    //   $scope.user.bananas -= cost;
    //   //console.log(cost, ' bananas spent');

    //   //Update backend through API

    // }
    // else
    // {
    //   console.log('Not enough bananas');
    // }

  };

}

function user_ctrl($scope, Restangular)
{
  $scope.display_login = false;
  //CODE OUTLINE
  //Get User Data
    //If fails
      //Login
      //Get User Data

  // Get back the username and the no of bananas
  Restangular.all('user').getList().then(function (results) {
    console.log("User logged in");
    $scope.user = results;
  },
  function() {
    console.log("User Not Logged in, showing login page");
    $scope.display_login = true;

  });

  $scope.login = function () {
    Restangular.all('user').customPOST('login', {}, {}, {username: $scope.user.username, password: $scope.user.password}).then(function (results) {
      console.log("user logged in");
      $scope.user = results.data;
      //Need to pull health from API

      $scope.display_login = false;
    },
    function (results) {
      console.log(results.data.data.error);
      console.log("Login Failed");
      $scope.login_failed = true;
    });
  }

  $scope.logout = function () {
    Restangular.all('user').customPOST('logout').then( function (results) {
      $scope.display_login = true;
      console.log("User Logout done");
    },
    function (results) {
      console.log("User Logout failed");
    })
  }



  

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

 