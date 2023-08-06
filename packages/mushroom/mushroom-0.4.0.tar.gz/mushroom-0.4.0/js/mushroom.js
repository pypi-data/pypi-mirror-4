(function(undefined) {

/**
 * Check if value is undefined and return the defaultValue in this case.
 * @param value {Any} value to check if it is undefined
 * @param defaultValue {Any} fallback value if `value` is undefined
 * @returns {Any} value if value is not undefined or the default value
 */
function default_if_undefined(value, defaultValue) {
	return value !== undefined
		? value
		: defaultValue;
}

// create empty mushroom namespace
var mushroom = window.mushroom;
if (mushroom === undefined) {
	mushroom = window.mushroom = {};
}

/**
 * Base class for all exceptions.
 */
mushroom.Exception = function(message) {
	this.message = message;
}

mushroom.Exception.prototype = new Error();
mushroom.Exception.prototype.name = 'mushroom.Exception';

/**
 * This exception is thrown when trying to call an operation on an
 * object which is currently in the wrong state.
 */
mushroom.IllegalState = function(message) {
	this.message = message;
}

mushroom.IllegalState.prototype = new mushroom.Exception();
mushroom.IllegalState.prototype.name = 'mushroom.IllegalState';

/**
 * This exception is sent when an error occures while trying to
 * connect to the server.
 */
mushroom.ConnectionError = function(message) {
	this.message = message;
}

mushroom.ConnectionError.prototype = new mushroom.Exception();
mushroom.ConnectionError.prototype.name = 'mushroom.ConnectionError';

/**
 * This exception is sent when an error response is received for
 * which no error handler is registered.
 * @param request {Object} request object as sent from the client
 * @param response {Object} error response object as received from
 *     the server
 */
mushroom.RequestFailed = function(request, response) {
	this.message = 'Method call failed: ' + request.method;
	this.request = request;
	this.response = response;
}

mushroom.RequestFailed.prototype = new mushroom.Exception();
mushroom.RequestFailed.prototype.name = 'mushroom.RequestFailed';

/**
 * Signal class which allows distribution of signals. This class is
 * used by the mushroom Client class to notify the user code about
 * various state changes.
 */
mushroom.Signal = function Signal() {
	this.handlers = [];
};

/**
 * Send event to all connected handlers.
 * This function takes any number of arguments which are
 * passed 1:1 to the connected handler functions.
 */
mushroom.Signal.prototype.send = function() {
	var args = arguments;
	this.handlers.forEach(function(handler) {
		handler.apply(this, args);
	}.bind(this));
};

/**
 * Connect a handler to the signal. The handler will be called with
 * the same arguments that are given to the Signal.send() function.
 * @param handler {Function} handler the handler to be connected
 */
mushroom.Signal.prototype.connect = function(handler) {
	this.handlers.push(handler);
};

/**
 * Disconnect handler from the signal. After disconnecting the handler
 * it will no longer receive events from the signal. Calling disconnect
 * on a handler that is not connected is silently ignored.
 * @param {Function} handler the handler to be disconnected
 */
mushroom.Signal.prototype.disconnect = function(handler) {
	var index = this.handlers.indexOf(handler);
	if (index !== -1) {
		this.handlers.splice(index, 1);
	}
};

/**
 * Disconnect all handlers.
 */
mushroom.Signal.prototype.disconnectAll = function() {
	this.handlers.splice(0);
};

function createXHR() {
	try {
		return new window.XMLHttpRequest();
	} catch(e) {};
	try {
		return new window.ActiveXObject('Microsoft.XMLHTTP');
	} catch(e) {};
}

var WEB_SOCKET_SUPPORT = 'WebSocket' in window;

function post(url, data, callback, errorCallback) {
	var xhr = createXHR();
	xhr.open('POST', url, true);
	xhr.onreadystatechange = function() {
		if (xhr.readyState === 4) {
			if (xhr.status == 200) {
				callback(xhr);
			} else {
				errorCallback(xhr);
			}
		}
	};
	/* In order to make so called 'simple requests' that work via CORS
	 * the Content-Type is very limited. We simply use text/plain which
	 * is better than using form-data content types.
	 * https://developer.mozilla.org/en/http_access_control#Simple_requests
	 */
	if (data != null) {
		xhr.setRequestHeader('Content-Type', 'text/plain')
		xhr.send(JSON.stringify(data));
	} else {
		xhr.send(null);
	}
}


/**
 * The mushroom client class.
 * @param {Object} options
 */
mushroom.Client = function(options) {
	this.url = options.url;
	this.transports = options.transports ||
			(WEB_SOCKET_SUPPORT ? ['ws', 'poll'] : ['poll']);
	this.transport = null;
	this.methods = options.methods || {};
	this.queue = new mushroom.MessageQueue();
	this.requests = {};

	this.signals = {
		// This signal is sent when a request returns an error and
		// no errorCallback was specified.
		error: new mushroom.Signal(),
		// This signal is sent when the connection is established.
		connected: new mushroom.Signal(),
		// This signal is sent when the connection was terminated.
		disconnected: new mushroom.Signal()
	};

	// FIXME this requires jQuery
	/*
	$(window).bind('beforeunload', function() {
		// FIXME It seams that this call should be done asynchroneously
		//       which might not work for cross domain requests at all.
		//       We need to find a good solution here or use a shorter
		//       timeout value in order to detect disconnects earlier at
		//       the server side.
		this.disconnect();
	}.bind(this));
	*/
}

/**
 * Start connecting to remote server. This function is asynchroneous and
 * upon connection success the `connected` signal is sent.
 * @returns {undefined}
 */
mushroom.Client.prototype.connect = function(auth) {
	var request = {
		transports: this.transports,
		auth: auth || null
	}
	post(this.url, request, function(xhr) {
		jsonResponse = JSON.parse(xhr.responseText);
		transportClass = mushroom.transports[jsonResponse.transport];
		if (transportClass === undefined) {
			this.signals.error.send(new mushroom.ConnectionError(
					'Unsupported transport ' + this.transport));
			return;
		}
		this.transport = new transportClass(this, jsonResponse);
		this.transport.start();
	}.bind(this), function(xhr) {
		this.signals.error.send(new mushroom.ConnectionError(
				'Transport negotiation failed. Status code=' + xhr.status));
	}.bind(this));
};

/**
 * Disconnect client from server.
 * @throws
 */
mushroom.Client.prototype.disconnect = function() {
	// FIXME check current state of transport
	this.sendMessage(new mushroom.Disconnect({}));
};

/**
 * Register a client method
 * @param name {String} name of the method
 * @param callback {Function} callback function which should
 *     handle method calls for this method name
 */
mushroom.Client.prototype.method = function(name, callback) {
	this.methods[name] = callback;
	return this;
};

/**
 * Send notification to the server.
 * @param method {String} name of the method to be called
 * @param data {Any} data the request data
 */
mushroom.Client.prototype.notify = function(method, data) {
	var notification = new mushroom.Notification({
		method: method,
		data: data
	});
	this.queue.push(notification);
	this.sendMessage(notification);
};

/**
 * Retrieve request object from requests object while
 * removing it from there. This method is used to retrieve
 * the request object when receiving a response or error.
 */
mushroom.Client.prototype.popRequest = function(id) {
	var request = this.requests[id];
	delete this.requests[id];
	return request;
};

/**
 * Send request to the server.
 * @param method {String} name of the method to be called
 * @param data {Any} data the request data
 * @param responseCallback {Function} callback which is called
 *     when the response is received.
 * @param errorCallback {Function} callback which is called
 *     when an error response is received. If no callback is
 *     provided the global error signal is used instead.
 */
mushroom.Client.prototype.request = function(method, data, responseCallback, errorCallback) {
	if (responseCallback === undefined) {
		throw Error("responseCallback is mandatory");
	}
	var request = new mushroom.Request({
		method: method,
		data: data,
		responseCallback: responseCallback,
		errorCallback: errorCallback
	});
	this.queue.push(request);
	this.requests[request.messageId] = request;
	this.sendMessage(request);
};

/**
 * Send message
 * @param message {Object}
 */
mushroom.Client.prototype.sendMessage = function(message) {
	if (this.transport !== null && this.transport.connected) {
		this.transport.sendMessage(message);
	}
};

/**
 * Handle a notification received from the server
 * @param notification {Object}
 */
mushroom.Client.prototype.handleNotification = function(notification) {
	var method = this.methods[notification.method];
	if (method !== undefined) {
		method.call(this, notification);
	} else {
		this.error.signal(new mushroom.Exception(
				'No method for notification: ' + notification.method));
	}
}

/**
 * Handle a response received from the server
 * @param response {Object}
 */
mushroom.Client.prototype.handleResponse = function(response) {
	var request = this.popRequest(response.requestMessageId);
	request.responseCallback(response.data);
}

/**
 * Handle an error response received from the server.
 * @param error {Object}
 */
mushroom.Client.prototype.handleError = function(error) {
	var request = this.popRequest(error.requestMessageId);
	if (errorCallback === undefined) {
		// No errorCallback given. Send an error signal.
		this.signals.error.send(new mushroom.RequestFailed(
				request, error));
	} else {
		request.errorCallback(error.data);
	}
}

/**
 * Handle a disconnect message received from the server.
 */
mushroom.Client.prototype.handleDisconnect = function() {
	this.transport = null;
	this.signals.disconnected.send()
}

/**
 * Message queue class for outbound messages. This class is used to queue
 * outbound messages until they are acknowledged by the server. If the
 * connection is lost before the message has been acknowledged it will be
 * retransmitted as soon as the connection is reestablished.
 */
mushroom.MessageQueue = function() {
	this.nextMessageId = 0;
	this.messages = [];
}

/**
 * Add message to the queue.
 * @param message {Object} object to be added
 * @returns {Number} message id of the added message
 */
mushroom.MessageQueue.prototype.push = function(message) {
	if (message.messageId !== null) {
		throw new mushroom.Exception('Message does already have a message id');
	}
	message.messageId = this.nextMessageId;
	this.messages.push(message);
	this.nextMessageId += 1;
	return message.messageId;
};

/**
 * Acknowledge messages. This removes all messages with with a
 * messageId less or equal than the given messageId from the queue.
 * @param messageId {Number}
 */
mushroom.MessageQueue.prototype.ack = function(messageId) {
	if (messageId >= this.nextMessageId) {
		throw new mushroom.Exception('Can not acknowledge a message id that was never part of this queue');
	}
	var i, message;
	for (var i=0; i<this.messages.length; ++i) {
		message = this.messages[i];
		if (message.messageId > messageId) {
			// First message found which is not acknowledged.
			break;
		}
	}
	this.messages.splice(0, i);
};

/**
 * Call function for every message in the queue.
 * @param f {Function} the function to be called
 */
mushroom.MessageQueue.prototype.forEach = function(f) {
	var i, message;
	for (var i=0; i<this.messages.length; ++i) {
		message = this.messages[i];
		f(message);
	}
};

/**
 * Constants for the state of the client and its transport.
 *
 *        .------> [DISCONNECTED] ------.
 *        |              ^   ^          |
 *        |              |   |          |
 * [DISCONNECTING]       |   |      connect()
 *        |              |   |          |
 *        |              |   |          |
 *        |              |   |          v
 *   disconnect()        |   '---- [CONNECTING]
 *        |              |              |
 *        |              |              |
 *        '-------- [CONNECTED] <-------'
 *
 */
mushroom.STATE = {
	CONNECTING: 'CONNECTING',
	CONNECTED: 'CONNECTED',
	DISCONNECTING: 'DISCONNECTING',
	DISCONNECTED: 'DISCONNECTED'
};

/**
 * Transport for the HTTP poll protocol.
 * @param client {mushroom.Client} The client object which is notified
 *     about inbound messages and state changes of the transport
 * @param options {Object}
 */
mushroom.PollTransport = function(client, options) {
	this.client = client;
	this.url = options.url;
	this.lastMessageId = null;
	this.running = false;
	this.stopping = false;
	this.connected = false;
	// FIXME implement new states
}

/**
 * Start the poll transport. This causes the transport to send poll
 * requests until either the client or the server sides decides to
 * disconnect or a timeout happens.
 */
mushroom.PollTransport.prototype.start = function() {
	if (this.running) {
		throw new mushroom.IllegalState('Already started');
	}
	this.poll();
};

/**
 * Perform a poll request.
 */
mushroom.PollTransport.prototype.poll = function() {
	this.running = true;
	this.connected = true;
	this.client.signals.connected.send();
	var request = [
		[0, this.lastMessageId]
	]
	post(this.url, request, function(xhr) {
		data = JSON.parse(xhr.responseText);
		data.forEach(function(messageData) {
			var message = mushroom.messageFromData(messageData);
			if ('messageId' in message) {
				if (message.messageId <= this.lastMessageId &&
						this.lastMessageId !== null) {
					// skip messages which we have already processed
					return;
				}
				this.lastMessageId = message.messageId;
			}
			message_name = message.constructor.MESSAGE_NAME;
			var handler = this.client['handle' + message_name];
			handler.call(this.client, message);
		}.bind(this));
		if (this.stopping) {
			this.stopping = false;
			this.running = false;
		} else {
			this.poll();
		}
	}.bind(this), function(xhr) {
		this.running = false;
		this.stopping = false;
		this.connected = false;
		this.client.handleDisconnect();
	}.bind(this));
};

/**
 * Send message to the server.
 */
mushroom.PollTransport.prototype.sendMessage = function(message) {
	// FIXME
	// Add a browser timeout so it is possible to send two or more
	// messages at the same time. Also make sure to check if there
	// is already a send request running.
	var request = [
		message.toList()
	];
	post(this.url, request, function(xhr) {
		// FIXME remove message from out-queue
	}.bind(this), function(xhr) {
		// FIXME log error
	}.bind(this));
}

/**
 * The WebSocket transport
 * @param client {mushroom.Client} The client object which is notified
 *     about inbound messages and state changes of the transport
 * @param options {Object}
 */
mushroom.WebSocketTransport = function(client, options) {
	this.client = client;
	this.url = options.url;
	this.connected = false;
	// FIXME implement new states
};

/**
 * Start the WebSocket transport. This causes the WebSocket transport
 * to connect to the server and stay connected.
 */
mushroom.WebSocketTransport.prototype.start = function() {
	this.ws = new WebSocket(this.url);
	this.ws.onopen = function(event) {
		this.connected = true;
		this.client.signals.connected.send();
		// XXX This is the same for all transports - move this logic
		//     into the client.
		this.client.queue.forEach(this.sendMessage.bind(this));
	}.bind(this);
	this.ws.onclose = function(event) {
		this.connected = false;
		this.client.handleDisconnect();
	}.bind(this);
	this.ws.onmessage = function(event) {
		frame = event.data;
		messageData = JSON.parse(frame);
		message = mushroom.messageFromData(messageData);
		if ('messageId' in message) {
			if (message.messageId <= this.lastMessageId &&
					this.lastMessageId !== null) {
				// skip messages which we have already processed
				return;
			}
			this.lastMessageId = message.messageId;
		}
		message_name = message.constructor.MESSAGE_NAME;
		var handler = this.client['handle' + message_name];
		handler.call(this.client, message);
	}.bind(this);
};

/**
 * Send message to the server.
 * @param message {Object}
 */
mushroom.WebSocketTransport.prototype.sendMessage = function(message) {
	var data = message.toList();
	var frame = JSON.stringify(data);
	this.ws.send(frame);
};

mushroom.transports = {
	'poll': mushroom.PollTransport,
	'ws': mushroom.WebSocketTransport
}

mushroom.Heartbeat = function(options) {
	this.client = options.client;
	this.lastMessageId = options.lastMessageId;
};

mushroom.Heartbeat.MESSAGE_CODE = 0;
mushroom.Heartbeat.MESSAGE_NAME = 'Heartbeat';

mushroom.Heartbeat.prototype.toList = function() {
	return [mushroom.Heartbeat.MESSAGE_CODE, this.lastMessageId];
};

mushroom.Notification = function(options) {
	this.client = options.client;
	this.messageId = default_if_undefined(options.messageId, null);
	this.method = options.method;
	this.data = options.data;
};

mushroom.Notification.MESSAGE_CODE = 1;
mushroom.Notification.MESSAGE_NAME = 'Notification';

mushroom.Notification.prototype.toList = function() {
	return [mushroom.Notification.MESSAGE_CODE, this.messageId,
			this.method, this.data];
};

mushroom.Request = function(options) {
	this.client = options.client;
	this.messageId = default_if_undefined(options.messageId, null);
	this.method = options.method;
	this.data = options.data || null;
	this.responseCallback = options.responseCallback;
	this.errorCallback = options.errorCallback;
};

mushroom.Request.MESSAGE_CODE = 2;
mushroom.Request.MESSAGE_NAME = 'Request';

mushroom.Request.prototype.toList = function() {
	return [mushroom.Request.MESSAGE_CODE, this.messageId,
			this.method, this.data];
}

mushroom.Request.prototype.sendResponse = function(data) {
	var response = new mushroom.Response({
		client: this.client,
		requestMessageId: this.messageId,
		data: data
	});
	this.client.queue.push(response);
	this.client.sendMessage(response);
};

mushroom.Request.prototype.sendError = function(data) {
	var error = new mushroom.Error({
		client: this.client,
		requestMessageId: this.messageId,
		data: data
	});
	this.client.queue.push(error);
	this.client.sendMessage(error);
}

mushroom.Response = function(options) {
	this.client = options.client;
	this.messageId = default_if_undefined(options.messageId, null);
	this.requestMessageId = options.requestMessageId;
	this.data = options.data || null;
};

mushroom.Response.MESSAGE_CODE = 3;
mushroom.Response.MESSAGE_NAME = 'Response'

mushroom.Response.prototype.success = true;

mushroom.Error = function(options) {
	this.client = options.client;
	this.messageId = default_if_undefined(options.messageId, null);
	this.requestMessageId = options.requestMessageId;
	this.data = options.data || null;
};

mushroom.Error.MESSAGE_CODE = 4;
mushroom.Error.MESSAGE_NAME = 'Error'

mushroom.Error.prototype.success = false;

mushroom.Error.prototype.toList = function() {
	return [mushroom.Error.MESSAGE_CODE, this.messageId,
			this.requestMessageId, this.data];
};

mushroom.Disconnect = function(options) {
	this.client = options.client;
};

mushroom.Disconnect.MESSAGE_CODE = -1;
mushroom.Disconnect.MESSAGE_NAME = -1;

mushroom.Disconnect.prototype.toList = function() {
	return [mushroom.Disconnect.MESSAGE_CODE];
};

mushroom.messageFromData = function(data) {
	switch (data[0]) {
		case 0: // heartbeat
			return new mushroom.Heartbeat({
				client: this,
				lastMessageId: data[1]
			});
		case 1: // notification
			return new mushroom.Notification({
				client: this,
				messageId: data[1],
				method: data[2],
				data: data[3]
			});
		case 2: // request
			return new mushroom.Request({
				client: this,
				messageId: data[1],
				method: data[2],
				data: data[3]
			});
		case 3: // response
			return new mushroom.Response({
				client: this,
				messageId: data[1],
				requestMessageId: data[2],
				data: data[3]
			});
		case 4: // error
			return new mushroom.Error({
				client: this,
				messageId: data[1],
				requestMessageId: data[2],
				data: data[3]
			});
		case -1: // disconnect
			return new mushroom.Disconnect({
				client: this
			});
		default:
			throw new mushroom.Exception(
					'Unsupported message code: ' + data[0])
	}
};

})();
