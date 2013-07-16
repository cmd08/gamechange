'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers', 'restangular']).
  config(function($routeProvider) {
    $routeProvider.when('/home', {templateUrl: '/static/bananas/partials/home.html', controller: 'MyCtrl1'});
    $routeProvider.when('/main_menu', {templateUrl: '/static/bananas/partials/main_menu.html', controller: 'MyCtrl2'});
    $routeProvider.when('/monkey_business', {templateUrl: '/static/bananas/partials/monkey_business.html', controller: 'MyCtrl3'});
    $routeProvider.when('/banana_run', {templateUrl: '/static/bananas/partials/banana_run.html', controller: 'MyCtrl4'});
    $routeProvider.otherwise({redirectTo: '/home'});
  }).
  config(function(RestangularProvider) {
  	RestangularProvider.setBaseUrl("/bananas/api");


    // This function is used to map the JSON data to something Restangular
    // expects
    RestangularProvider.setResponseExtractor(function(response, operation, what, url) {
        if (operation === "getList") {
            // Use results as the return type, and save the result metadata
            // in _resultmeta
            var newResponse = response.data;
            newResponse._resultmeta = {
                "apiversion": response.apiversion,
                "debug": response.debug,
                "hostname": response.hostname,
                "systemtimemillis": response.systemtimemillis,
            };
            return newResponse;
        }

        return response;
    });

  });
