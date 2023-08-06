var global = this;
var jsError = null;
var client = null;
var transport = null;

function log(text) {
	var logElem = document.getElementById('log');
	var li = document.createElement('li');
	li.innerHTML = text;
	logElem.appendChild(li);
}

global.onerror = function(msg) {
	global.jsError = msg;
	log('onerror handler: ' + msg);
}


function test(name, f) {
	global[name] = function(cb) {
		var titleElem = document.getElementById('title');
		titleElem.innerHTML = name;
		var transportElem = document.getElementById('transport');
		transportElem.innerHTML = transport;
		f({
			ok: function(message) {
				if (message) {
					log('OK: ' + message);
				} else {
					log('OK');
				}
				cb(true);
			},
			error: function(message) {
				if (message) {
					log('Error: ' + message);
				} else {
					log('Error');
				}
				cb(message);
			}
		});
	};
}


test('test_connect', function(result) {
	client = new mushroom.Client({
		url: '/',
		transports: [transport]
	});
	client.signals.connected.connect(function() {
		result.ok();
	});
	client.signals.error.connect(function() {
		result.error();
	});
	client.connect();
});


test('test_connect_server_offline', function(result) {
	client = new mushroom.Client({
		url: 'http://127.0.0.1:65535/',
		transports: [transport]
	});
	client.signals.connected.connect(function() {
		client.disconnect();
		result.error();
	});
	client.signals.error.connect(function() {
		result.ok();
	});
	client.connect();
});


test('test_send_request', function(result) {
	client = new mushroom.Client({
		url: '/',
		transports: [transport]
	});
	client.connect();
	client.request('test_request', null, function(data) {
		if (data == 42) {
			result.ok();
		} else {
			result.error('Wrong answer received: ' + data);
		}
	}, function(data) {
		result.error('Error response received: ' + data);
	});
});


test('test_send_notification', function(result) {
	client = new mushroom.Client({
		url: '/',
		transports: [transport]
	});
	client.connect();
	client.notify('test_notification', null);
	result.ok();
});


test('test_disconnect_1', function(result) {
	client = new mushroom.Client({
		url: '/',
		transports: [transport]
	});
	client.signals.connected.connect(function() {
		result.ok('connected');
	});
	client.connect();
});

test('test_disconnect_2', function(result) {
	client.signals.disconnected.connect(function() {
		result.ok('disconnected');
	});
	client.disconnect();
});
