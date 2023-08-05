//
// Binding for CometD that uses pure browser features, no toolkits.
//
// Copyright (c) The Dojo Foundation 2011. All Rights Reserved.
// Copyright (c) IBM Corporation 2008, 2011. All Rights Reserved.
//
/*jslint white:false, bitwise:true, eqeqeq:true, immed:true, nomen:false, 
  onevar:false, plusplus:false, undef:true, browser:true, devel:true, 
  forin:false, sub:false*/
/*global define */
define([
    'coweb/util/xhr',
    'org/cometd',
    'org/cometd/AckExtension',
	'org/requirejs/i18n!../../nls/messages'
], function(xhr, cometd, AckExtension, messages) {
    // use browser native functions, http://caniuse.com/#search=JSON
    cometd.JSON.toJSON = JSON.stringify;
    cometd.JSON.fromJSON = JSON.parse;
    
    // build default instance
    var c = new cometd.Cometd();

    // implement abstract methods in required transports
    var LongPollingTransport = function() {
        var _super = new cometd.LongPollingTransport();
        var that = cometd.Transport.derive(_super);
        // implement abstract method
        that.xhrSend = function(packet) {
            packet.method = 'POST';
            packet.headers = packet.headers || {};
            packet.headers['Content-Type'] = 'application/json;charset=UTF-8';
            packet.headers['Cache-Control'] = 'no-cache';
            var promise = xhr.send(packet);
            promise.then(function(args) {
                packet.onSuccess(args.xhr.responseText);
            }, function(args) {
                var err = new Error(messages.failedloading +' '+args.url+' status: '+args.xhr.status);
                packet.onError(args.xhr.statusText, err);
            });
            return promise.xhr;
        };
        return that;
    };

    // register transports
    if (cowebConfig.useWebSockets) {
    	c.registerTransport('websocket', new org.cometd.WebSocketTransport());
    } else {
    	c.registerTransport('long-polling', new LongPollingTransport());
    }
    
    // register required extension
    c.registerExtension('ack', new AckExtension());
    return c;
});
