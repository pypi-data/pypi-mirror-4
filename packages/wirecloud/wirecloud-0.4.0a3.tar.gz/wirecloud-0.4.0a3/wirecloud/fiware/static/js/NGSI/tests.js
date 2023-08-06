(function () {
    var ajaxMockFactory = {
        'createFunction': function createFunction() {
            var func, instance;

            instance = {};

            func = function (url, options) {
                var response_info;

                if (options == null) {
                    options = {};
                }

                if (url in this.staticURLs) {
                    response_info = this.staticURLs[url];
                    switch (typeof response_info.checkRequestContent) {
                    case "string":
                        if (response_info.checkRequestContent !== options.postBody) {
                            response_info = {
                                status_code: 400,
                                responseText: ""
                            };
                        }
                        break;
                    case "function":
                        if (!response_info.checkRequestContent(url, options)) {
                            response_info = {
                                status_code: 400,
                                responseText: ""
                            };
                        }
                        break;
                    default:
                    }
                }

                if (response_info != null) {

                    specific_callback = 'on' + response_info.status_code;

                    if (specific_callback in options) {
                        options[specific_callback]();
                    } else if (typeof options.onSuccess === 'function' && response_info.status_code >= 200 && response_info.status_code < 300) {
                        try {
                            options.onSuccess(response_info);
                        } catch (e) {}
                    } else if (typeof options.onFailure === 'function') {
                        try {
                            options.onFailure(response_info);
                        } catch (e) {}
                    }
                } else {
                    if (typeof options.onFailure === 'function') {
                        try {
                            options.onFailure({
                                status_code: 0
                            });
                        } catch (e) {}
                    }
                }

                if (typeof options.onComplete === 'function') {
                    try {
                        options.onComplete();
                    } catch (e) {}
                }

            };

            instance.staticURLs = {};
            instance.responseHandlers = {};

            // TODO
            var request = new XMLHttpRequest();
            request.open('GET', 'responses/query1.xml', false);
            request.send();
            instance.staticURLs["http://ngsi.server.com/ngsi10/queryContext"] = {
                status_code: 200,
                responseText: request.responseText
            };

            request = new XMLHttpRequest();
            request.open('GET', 'responses/update1.xml', false);
            request.send();
            instance.staticURLs["http://ngsi.server.com/ngsi10/updateContext"] = {
                status_code: 200,
                responseText: request.responseText
            };

            return func.bind(instance);
        }
    };

    window.ajaxMockFactory = ajaxMockFactory;
})();

describe("NGSI Library handles", function () {

    var connection, response, response_data;

    connection = new NGSI.Connection('http://ngsi.server.com', {
        requestFunction: ajaxMockFactory.createFunction()
    });

    beforeEach(function () {
        response = false;
        response_data = null;
    });

    it("basic query requests", function () {

        runs(function () {
            connection.query([
                {type: 'Technician', id: 'entity1'}
            ], null, {
                onSuccess: function (data) {
                    response_data = data;
                },
                onComplete: function () {
                    response = true;
                }
            })
        });

        waitsFor(function () {
            return response;
        },"Waiting NGSI response", 300);

        runs(function () {
            expect(response_data).toEqual({
                'tech1': {
                    'entity': {
                        'id': 'tech1',
                        'type': 'Technician'
                    },
                    'attributes': {
                        'email': {
                            'name': 'email',
                            'type': 'string',
                            'contextValue': 'jacinto.salas@mycompany.com'
                        },
                        'function': {
                            'name': 'function',
                            'type': 'string',
                            'contextValue': 'MV Keeper'
                        },
                        'mobile_phone': {
                            'name': 'mobile_phone',
                            'type': 'string',
                            'contextValue': '0034123456789'
                        },
                        'name': {
                            'name': 'name',
                            'type': 'string',
                            'contextValue': 'Jacinto Salas Torres'
                        },
                        'twitter': {
                            'name': 'twitter',
                            'type': 'string',
                            'contextValue': 'jsalas'
                        },
                        'van': {
                            'name': 'van',
                            'type': 'string',
                            'contextValue': 'van1'
                        },
                        'working_area': {
                            'name': 'working_area',
                            'type': 'integer',
                            'contextValue': '28050'
                        }
                    }
                }
            });
        });
    });

    it("basic query requests using the flat option", function () {

        runs(function () {
            connection.query([
                {type: 'Technician', id: 'entity1'}
            ], null, {
                flat: true,
                onSuccess: function (data) {
                    response_data = data;
                },
                onComplete: function () {
                    response = true;
                }
            })
        });

        waitsFor(function () {
            return response;
        },"Waiting NGSI response", 300);

        runs(function () {
            expect(response_data).toEqual({
                tech1: {
                    'id': 'tech1',
                    'type': 'Technician',
                    'email': 'jacinto.salas@mycompany.com',
                    'function': 'MV Keeper',
                    'mobile_phone': '0034123456789',
                    'name': 'Jacinto Salas Torres',
                    'twitter': 'jsalas',
                    'van': 'van1',
                    'working_area': '28050'
                }
            });
        });
    });

    it("basic update context requests", function () {

        runs(function () {
            connection.updateAttributes([
                {
                    'entity': {type: 'Technician', id: 'entity1'},
                    'attributes': {
                        'name': 'mobile_phone',
                        'type': 'string',
                        'contextValue': '0034223456789'
                    }
                }
            ], {
                onSuccess: function (data) {
                    response_data = data;
                },
                onComplete: function () {
                    response = true;
                }
            })
        });

        waitsFor(function () {
            return response;
        },"Waiting NGSI response", 300);

        runs(function () {
            expect(response_data).toEqual({
                'tech1': {
                    'entity': {
                        'id': 'tech1',
                        'type': 'Technician'
                    },
                    'attributes': {
                        'mobile_phone': {
                            'name': 'mobile_phone',
                            'type': 'string',
                            'contextValue': '0034223456789'
                        }
                    }
                }
            });
        });
    });

    it("basic update context requests using the flat option", function () {

        runs(function () {
            connection.updateAttributes([
                {
                    'entity': {type: 'Technician', id: 'entity1'},
                    'attributes': {
                        'name': 'mobile_phone',
                        'type': 'string',
                        'contextValue': '0034223456789'
                    }
                }
            ], {
                flat: true,
                onSuccess: function (data) {
                    response_data = data;
                },
                onComplete: function () {
                    response = true;
                }
            })
        });

        waitsFor(function () {
            return response;
        },"Waiting NGSI response", 300);

        runs(function () {
            expect(response_data).toEqual({
                'tech1': {
                    'id': 'tech1',
                    'type': 'Technician',
                    'mobile_phone': '0034223456789'
                }
            });
        });
    });
});
