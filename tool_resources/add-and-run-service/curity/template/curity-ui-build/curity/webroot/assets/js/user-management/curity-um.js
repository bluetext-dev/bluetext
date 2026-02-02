/*
 * Copyright (C) 2016 Curity AB. All rights reserved.
 *
 * The contents of this file are the property of Curity AB.
 * You may not copy or use this file, in either source code
 * or executable form, except in compliance with terms
 * set by Curity AB.
 *
 * For further information, please contact Curity AB.
 */

var um = {'client' : {}, "assistedSettings" : {}, "umSettings" : {}};

um.assistedSettings = {
    //TODO this perhaps is not static?
    clientId: "um-client",
    autoPrepareJqueryAjax: true,
    for_origin : ''
};

//This will not change so it can be a constant here.
um.umSettings.singleUserTemplate = "fragments/um-single-user";


um.client = function(baseUrl, viewsEndpointBasePath, dataEndpointBasePath) {

    um.assistedSettings.for_origin = baseUrl;
    var assistant = curity.token.assistant(um.assistedSettings);

    var getViewsPath = function (path) {
        var newPath = path;
        if(!path.startsWith("/")) {
            newPath = "/" + path;
        }
        return baseUrl + viewsEndpointBasePath + newPath;
    };

    var getDataPath = function (path) {
        var newPath = path;
        if(!path.startsWith("/")) {
            newPath = "/" + path;
        }
        return baseUrl + dataEndpointBasePath + newPath;
    };

    var showError = function(err) {
        $("#errors").html("<div class='alert alert-danger'>" + err.error_description + "</div>");
    };

    var loadPage = function(page, target) {
        var deferred = $.Deferred();
        var url = getViewsPath(page);
        assistant.prepareJQuery($);
        $.get(url).done(function(data) {
            $(target).html(data);
            deferred.resolve();
        }).fail(function(err) {
            console.log("Failed to load fragment", err);
            deferred.reject(err);
        });
        return deferred.promise();
    };


    var authenticate = function() {
        var deferred = $.Deferred();
        assistant.fetchTokensOrLogin(true)
            .then(function(){
                //Load page
                console.log("Loading page");
                loadPage(um.umSettings.singleUserTemplate, "#edit-form")
                    .done(deferred.resolve)
                    .fail(deferred.reject);
            })
            .fail(function(err){
                //Show error
                console.error("Failed to authenticate ", err);
                showError(err);
                deferred.reject(err);
            });
        return deferred.promise();
    };

    var fetchData = function(path) {
        var deferred = $.Deferred();
        var fullPath = getDataPath(path);
        //TODO check authenticated first.
        $.ajax({
            url : fullPath,
            dataType : 'json'
        }).done(function(data) {
            deferred.resolve(data);
        }).fail(function(err) {
            deferred.reject(err);
        });
        return deferred.promise();
    };

    return {
        'authenticate' : authenticate,
        'get'          : fetchData
    }
};
