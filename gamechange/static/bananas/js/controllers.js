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

function userinfo_ctrl ($scope, Restangular){
  // $scope.user.bananas = response.data.user.bananas
}

function banana_run_ctrl ($scope, $location, Restangular)
{
  Restangular.all('healthgraph').getList().then(function (results) {
    $scope.activities = results;
    console.log($scope.activities );
  },
  function(results) {
    console.log('Healthgraph error');
    // console.log(results);
    // console.log(results.data.data);
    if (results.data.data.redirect == "/api/healthgraph/authorize")
    {
      console.log("Need to redirect to authorise page");
      $location.path('/banana_run_auth');
    }
  });
  // $scope.$apply(function (){
  $scope.bank = function(activity_id) {
    console.log("BANK!")
    Restangular.one('healthgraph', activity_id).customPOST('bank').then(function (response){
      console.log(response.data);
      for(var i=0;i<$scope.activities.length;i++){
        if($scope.activities[i].id===response.data.id){
          $scope.activities[i].banked=response.data.banked;
          break;
        }
      }
    });
    Restangular.one('user').get().then(function(response){
      console.log(response.data);
      $scope.user.bananas = response.data.bananas;
    });
  };
  // });
   
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
        $scope.user.bananas = response.data.bananas;
        $scope.user.inventory = response.data.inventory;
        $scope.user.item_count = response.data.item_count;
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

function user_ctrl($scope, Restangular, dialogService)
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
    $scope.user.health = results.data.health;
    $scope.user.item_count = results.item_count;
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
        $scope.user.health = results.data.health;
        $scope.user.item_count = results.data.item_count;
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

    Restangular.one('user/inventory', item.item.id).customPOST('use').then(function(results){
      Restangular.one('user').get().then(function(response){
        console.log(response.data);
        $scope.user = response.data; 
        $scope.user.health = response.data.health;
        $scope.user.inventory = response.data.inventory;
        $scope.user.item_count = response.data.item_count;
      });
    },
    function (results) {
        console.log(results.data.data.error);
        if (results.data.data.error == "Your health is already at maximum")
        {
          // dialogService.showDialog();
          // dialogService.showMessage('Record not Found!', 'The record you were looking for cannot be found.');
          $scope.max_health = true;
          $scope.show_alert = true;
    //       var dialogOptions = {
    //     closeText: 'Cancel',
    //     actionText: 'Delete Timesheet',
    //     header: 'Delete Timesheet?',
    //     body: 'Are you sure you want to delete this timesheet?',
    //     callback: function () {
    //         recordsService.delete($scope.record.id)
    //             .success(function (opStatus) {
    //                 if (opStatus.status) {
    //                     $location.path('/records');
    //                 }
    //                 else {
    //                     errorService.createErrorAlert($scope, 
    //                      'There was a problem deleting the timesheet: ' + error.message);
    //                 }
    //             })
    //             .error(function (error) {
    //                 errorService.createErrorAlert($scope, 'Error deleting record: ' + error.message);
    //             });
    //     }
    // };

        dialogService.showDialog({}, {});
        }
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

function DialogDemoCtrl($scope, $dialog) {

    // Inlined template for demo
    var t = '<div class="modal-header">' +
            '<h3>Maximum Health Reached</h3>' +
            '</div>' +
            '<div class="modal-body">' +
            '<p>You have already reached the maximum health</p>' +
            '</div>' +
            '<div class="modal-footer">' +
            '<button ng-click="close()" class="btn btn-primary" >Close</button>' +
            '</div>';

    $scope.opts = {
        backdrop: true,
        keyboard: true,
        backdropClick: true,
        template: t, // OR: templateUrl: 'path/to/view.html',
        controller: 'TestDialogController'
    };

    var d = $dialog.dialog($scope.opts);
        d.open().then(function () {
        });
    // function () {
    //     var d = $dialog.dialog($scope.opts);
    //     d.open().then(function () {
    //     });
    // };
}

function TestDialogController($scope, dialog) {
    $scope.close = function () {
        dialog.close();
    };
}

// function alert_modal_ctrl($scope, $dialog, $log) {


//   $scope.open = function () {

//     var msg = 'Hello World!';
//     var t = '<div class="modal-header">' +
//             '<h3>This is the title</h3>' +
//             '</div>' +
//             '<div class="modal-body">' +
//             '<p>Enter a value to pass to <code>close</code> as the result: <input ng-model="result" /></p>' +
//             '</div>' +
//             '<div class="modal-footer">' +
//             '<button ng-click="close(result)" class="btn btn-primary" >Close</button>' +
//             '</div>';
//     var options = {
//       resolve: {
//         msg: function () { return msg; },
//         template: t
//       }
//     };

//     var dialog = $dialog.dialog(options);
    
//     dialog.open('dialog.html', 'DialogCtrl');
//     $log.info('Modal dismissed at: ' + new Date());
//   }
//   // console.log("open...")

//     // modalInstance.result.then(function () {
//     // }, function () {
      
//     // });
// };

// var DialogCtrl = function ($scope, $dialog, msg) {
//   $scope.msg = msg;
// };

$(function(){
    $("[data-hide]").on("click", function(){
       // $("." + $(this).attr("data-hide")).hide();
        // -or-, see below
       $(this).closest("." + $(this).attr("data-hide")).hide();
    });
});

$(function(){
    $("[data-show]").on("load", function(){
       $("." + $(this).attr("data-show")).show();
        // -or-, see below
       // $(this).closest("." + $(this).attr("data-show")).show();
    });
});
 