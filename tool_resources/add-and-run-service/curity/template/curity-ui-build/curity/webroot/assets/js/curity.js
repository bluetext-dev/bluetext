/*
 * Copyright (C) 2015 Curity AB. All rights reserved.
 *
 * The contents of this file are the property of Curity AB.
 * You may not copy or use this file, in either source code
 * or executable form, except in compliance with terms
 * set by Curity AB.
 *
 * For further information, please contact Curity AB.
 */

var se = {'curity': {'utils': {'poller': {}, 'transmeta': {}}}};

se.curity.utils.poller.startPolling = function startPoll(startPollTime, pollSettings)
{
    function requireFunction(fn, name) {
        if (typeof fn !== 'function') {
            throw new Error(name + ' is not a function');
        }
        return fn;
    }

    var intervalId = undefined;
    var pollTime = 1;
    var pollInterval = pollSettings.pollInterval;
    var maxWaitTime = pollSettings.maxWaitTime;
    var postUrl = pollSettings.url;
    var token;
    var onTimeout = requireFunction(pollSettings.onTimeout, 'onTimeout');
    var onFailure = requireFunction(pollSettings.onFailure, 'onFailure');
    var onSuccess = requireFunction(pollSettings.onSuccess, 'onSuccess');
    var onNotifyCompleted = pollSettings.onNotifyCompleted;
    var onMessage = pollSettings.onMessage;
    var iterations = 1;
    var stopPolling = false;
    var state = pollSettings.state;

    if (pollSettings.token != undefined)
    {
        token = "token=" + pollSettings.token;
    }

    function pollForAuthenticationEnd()
    {
        if (stopPolling)
        {
            return;
        }

        $.ajax({
            headers: {Accept: "application/json"},
            url: postUrl,
            method: "POST",
            data: { token: token, state: state } ,
            statusCode: {
                200: function ()
                {
                    //Not done yet... keep polling
                },
                201: function (data)
                {
                    if (data) {
                        if (data.stopPolling) {
                            stopPolling = true;
                        }

                        if (typeof onMessage === 'function') {
                            onMessage(data.message);
                        }
                    }
                },
                202: function ()
                {
                    stopPolling = true;
                    onSuccess();
                }
            }
        }).fail(function (err)
        {
            stopPolling = true;
            onFailure(err);

        }).done(function (data) {
            pollTime += pollInterval;
            iterations++;

            // Increase up to 5 seconds
            if ((pollInterval < 5) && (iterations % 3 === 0))
            {
                pollInterval += 1;
            }

            if (pollTime > maxWaitTime)
            {
                onTimeout();
            }
            else if (!stopPolling)
            {
                intervalId = window.setTimeout(pollForAuthenticationEnd, pollInterval * 1000);
            }
        });
    }

    intervalId = window.setTimeout(pollForAuthenticationEnd, startPollTime * 1000);

    $(document).on("visibilitychange", function()
    {
        if (document.visibilityState === "hidden")
        {
            stopPolling = true;
            window.clearInterval(intervalId);
        }
        else if (document.visibilityState === "visible")
        {
            var isIos = /iphone|ipod|ipad/i.test(navigator.userAgent);
            var isChromeIos = /crios/i.test(navigator.userAgent);
            var isFirefoxIos = /fxios/i.test(navigator.userAgent);
            if (isIos && !isChromeIos && !isFirefoxIos) {
                stopPolling = true;
                window.location.reload(true);
            }
            else {
                stopPolling = false;
            }

            intervalId = window.setTimeout(pollForAuthenticationEnd, 0);
        }
    });

    if (typeof onNotifyCompleted === 'function' && typeof window.BroadcastChannel === 'function') {
        const channel = new BroadcastChannel('se.curity.utils.poller.' + (pollSettings.name || ''));
        channel.onmessage = function () {
            stopPolling = true;
            onNotifyCompleted();
            channel.close();
        };
    }

    return function () {
        window.clearInterval(intervalId);
        stopPolling = true;
    };
};

se.curity.utils.poller.notifyCompleted = function (name) {
    if (typeof window.BroadcastChannel === 'function') {
        const channel = new BroadcastChannel('se.curity.utils.poller.' + (name || ''));
        channel.postMessage('');
        channel.close();
    }
};

se.curity.utils.transmeta = function (transactionMetaUrl, csrfToken)
{

    var get = function ()
    {
        var deferred = $.Deferred();

        $.ajax({
            url: transactionMetaUrl,
            method: "GET",
            beforeSend: function (xhr)
            {
                xhr.setRequestHeader('X-CSRF-TOKEN', csrfToken);
            }
        }).done(function (json)
        {
            return deferred.resolve(json);
        }).fail(function (err)
        {
            return deferred.reject(err);
        });

        return deferred.promise();
    };

    return {'get': get}
};
