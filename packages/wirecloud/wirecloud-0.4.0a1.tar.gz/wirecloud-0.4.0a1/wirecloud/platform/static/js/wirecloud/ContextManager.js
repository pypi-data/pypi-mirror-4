/*global Wirecloud*/

(function () {

    "use strict";

    var ContextManager = function ContextManager(contextInstance, initialContext) {
        Object.defineProperty(this, 'instance', {value: contextInstance});

        var context = initialContext;
        var handlers = [];

        Object.defineProperty(this, 'addCallback', {
            value: function addCallback(handler) {
                if (typeof handler !== 'function') {
                    throw new TypeError();
                }

                handlers.push(handler);
            }
        });

        Object.defineProperty(this, 'removeCallback', {
            value: function removeCallback(handler) {
                var index;

                if (typeof handler !== 'function') {
                    throw new TypeError();
                }

                index = handlers.indexOf(handler);
                if (index !== -1) {
                    handlers.splice(index, 1);
                }
            }
        });

        Object.defineProperty(this, 'get', {
            value: function get(key) {
                return context[key];
            }
        });

        Object.defineProperty(this, 'modify', {
            value: function get(values) {
                var key, i;

                if (typeof values !== 'object') {
                    throw new TypeError();
                }

                for (key in values) {
                    if (!context.hasOwnProperty(key)) {
                        throw new TypeError(key);
                    }
                }

                for (key in values) {
                    context[key] = values[key];
                }

                for (i = 0; i < handlers.length; i += 1) {
                    try {
                        handlers[i](values);
                    } catch (e) {}
                }
            }
        });
    };

    Wirecloud.ContextManager = ContextManager;

})();
