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

}])
.controller('MyCtrl5', [function() {

}]);

function banana_run_ctrl ($scope, Restangular)
{
  Restangular.all('healthgraph').getList().then(function (results) {
    $scope.activities = results;
    console.log($scope.activities );
  }),
  function(results) {
    console.log('Healthgraph error');
    console.log(results);
  }; 
}

function shop_products_ctrl($scope, Restangular)
{
  Restangular.all('shop').getList().then(function (results) {
    $scope.shop = results.items;
    //console.log($scope.shop );
  });

  $scope.buy = function(product) {
    console.log("BUY!");
    Restangular.one('shop', product.id).customPOST('buy').then(function(){
      Restangular.one('user').get().then(function(response){
        console.log(response.data);
        $scope.user = response.data;  
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
    $scope.user.health = Math.random() * 100;
  },
  function() {
    console.log("User Not Logged in, showing login page");
    $scope.display_login = true;

  });

  $scope.login = function () {
    //Need to check that username and password are not blank
    if ($scope.login_form.username.$error.required)
    {
      console.log("Blank Username Field");
      $scope.login_failed = true;
    }
    else if ($scope.login_form.password.$error.required)
    {
      console.log("Blank Password Field");
      $scope.login_failed = true;
    }
    else
    {
      Restangular.all('user').customPOST('login', {}, {}, {username: $scope.user.username, password: $scope.user.password}).then(function (results) {
        console.log("user logged in");
        $scope.user = results.data;
        $scope.user.health = Math.random() * 100;
        //Need to pull health from API

        $scope.display_login = false;
      },
      function (results) {
        console.log(results.data.data.error);
        console.log("Login Failed");
        $scope.login_failed = true;
      });
    }
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

  $scope.use_item = function(item) {
    console.log("Use item:");
    console.log(item);

    Restangular.one('user/inventory', item.inventory_id).customPOST('use').then(function(){
      Restangular.one('user').get().then(function(response){
        console.log(response.data);
        $scope.user = response.data;  
        $scope.user.health = Math.random() * 100;
      });
    });
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

 