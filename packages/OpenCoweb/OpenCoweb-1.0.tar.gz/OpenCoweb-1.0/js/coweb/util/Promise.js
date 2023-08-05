//
// Lightweight promises implementation loosely based on 
// http://wiki.commonjs.org/wiki/Promises/A and the dojo.Deferred 
// implementation.
//
// Copyright (c) The Dojo Foundation 2011. All Rights Reserved.
//
/*jslint white:false, bitwise:true, eqeqeq:true, immed:true, nomen:false, 
  onevar:false, plusplus:false, undef:true, browser:true, devel:true, 
  forin:false, sub:false*/
/*global define*/
define(['org/requirejs/i18n!../nls/messages'],function(messages) {
    /**
     * @class Promise
     * @constructor
     */
    var Promise = function() {
        // immutable properties
        var currListener, lastListener, result, errored, fulfilled;

        /**
         * Notify all listeners of the promise of success or failure.
         * 
         * @private
         * @returns {Boolean} True if any listener threw an uncaught error
         */
        var notifyListeners = function() {
            var func, rv, nextVal, ptr, unexpectedError = false;
            var success = function(ptr) {
                var promise = ptr.promise;
                return function(val) {
                    promise.resolve(val);
                };
            };
            var failure = function(err) {
                var promise = ptr.promise;
                return function(err) {                    
                    promise.fail(err);
                };
            };
            while(currListener) {
                ptr = currListener;
                currListener = currListener.next;
                func = (errored) ? ptr.errback : ptr.callback;
                if(func) {
                    // have a registered function for notification
                    try {
                        rv = func.call(ptr.context || this, result);
                        if(rv && typeof rv.then === 'function') {
                            // function returned a new promise
                            rv.then(success(ptr), failure(ptr), ptr.context);
                            continue;
                        }
                        // keep current value or use next
                        nextVal = (rv === undefined) ? result : rv;
                        if(rv instanceof Error) {
                            ptr.promise.fail(nextVal);
                        } else {
                            ptr.promise.resolve(nextVal);
                        }
                    } catch(e) {
                        if(typeof console !== 'undefined' && console.error) {
                            console.error(e, func);
                        }
                        // some registered function failed
                        ptr.promise.fail(e);
                        unexpectedError = true;
                    }
                } else {
                    // no registered function for notification
                    if(errored) {
                        ptr.promise.fail(result);
                    } else {
                        ptr.promise.resolve(result);
                    }
                }
            }
            return unexpectedError;
        };

        /**
         * Register listener(s) for promise resolution or failure.
         *
         * @param {Function} callback Invoked on resolution
         * @param {Function} errback Invoke on failure
         * @param {Object} context Optional context in which callback or 
         * errback is called
         * @returns {Promise} New promise of this promise's callback / 
         * errback resolution or failure  
         */
        this.then = function(callback, errback, context) {
            if(callback && typeof callback !== 'function') {
                callback = context[callback];
                if(typeof callback !== 'function') {
                    throw new Error(messages.callbackfunction);
                }
            }
            if(errback && typeof errback !== 'function') {
                errback = context[errback];
                if(typeof errback !== 'function') {
                    throw new Error(messages.errlbackfunction);
                }
            }
            var listener = {
                callback : callback,
                errback : errback,
                context : context,
                promise : new Promise()
            };
            if(currListener) {
                // attach this listener as next
                lastListener.next = listener;
                // this listener is now the last
                lastListener = listener;
            } else {
                // no listeners yet, this is the first
                currListener = lastListener = listener;
            }
            if(fulfilled) {
                notifyListeners();
            }
            return listener.promise;
        };

        /**
         * Resolve the promise.
         *
         * @param {any} value Any value
         * @return True if any listener threw an uncaught error
         */
        this.resolve = function(value) {
            if(fulfilled) {
                throw new Error(messages.promisealreadyresolved);
            }
            fulfilled = true;
            result = value;
            return notifyListeners();
        };

        /**
         * Fail the promise.
         *
         * @param {Error} err Error object
         * @return True if any listener threw an uncaught error
         */
        this.fail = function(err) {
            if(fulfilled) {
                throw new Error(messages.promisealreadyresolved);
            }
            fulfilled = true;
            errored = true;
            result = err;
            return notifyListeners();
        };
    };

    return Promise;
});