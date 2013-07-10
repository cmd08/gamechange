'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/home', {templateUrl: '/static/bananas/partials/home.html', controller: 'MyCtrl1'});
    $routeProvider.when('/main_menu', {templateUrl: '/static/bananas/partials/main_menu.html', controller: 'MyCtrl2'});
    $routeProvider.when('/monkey_business', {templateUrl: '/static/bananas/partials/monkey_business.html', controller: 'MyCtrl3'});
    $routeProvider.when('/banana_run', {templateUrl: '/static/bananas/partials/banana_run.html', controller: 'MyCtrl4'});
    $routeProvider.otherwise({redirectTo: '/home'});
  }]);
