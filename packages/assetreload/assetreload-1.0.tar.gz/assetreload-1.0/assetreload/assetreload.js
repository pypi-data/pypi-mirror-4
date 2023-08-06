function AssetReload(options) {
	options = options || {};

	var elements, element, data, i;
	var port = options.port || '8888';
	var webSocketUrl = 'ws://localhost:' + port + '/websocket?file='
										 + options.filesToWatch.join('&file=')
										 + '&host=' + window.location.href;

	var ws = new WebSocket(webSocketUrl);

	ws.onmessage = function(e) {
		data = JSON.parse(e.data);

		if (data.mimetype.match(/javascript/) ||
				window.location.pathname.match(data.path)) {
			window.location.reload();
			return;
		}

	  elements = document.querySelectorAll(
	  	'[href^="' + data.path + '"], [src^="' + data.path + '"]');
	  i = elements.length;

	  while (i--) {
	  	element = elements[i];
	  	attr = element.hasAttribute('href') ? 'href' : 'src';
			element.setAttribute(attr, data.path + '?' + Date.now());
	  }
	};
}
