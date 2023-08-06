(function AssetReload() {
    var elements, element, data, i;
    var script = document.getElementById('assetreload');
    var port = 8888;
    var connected = false;

    if (script.dataset.port) {
        port = script.dataset.port;
    }

    var ws = new WebSocket('ws://localhost:' + port + '/assetreload' +
                           '?host=' + window.location.href);

    ws.onopen = function() {
        connected = true;
    };

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

    ws.onclose = function() {
        if (!connected) {
            throw new Error('WebSocket connection failed. ' +
                            'Check that your port is configured correctly ' +
                            '(currently on ' + port + ')');
        }
    };
})();
