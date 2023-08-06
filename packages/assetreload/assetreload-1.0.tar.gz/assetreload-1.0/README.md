AssetReload
===========

AssetReload uses WebSockets to broadcast asset changes to the browser.


## Installation

Install with pip:

	pip install assetreload

If you don't have it installed, use `easy_install` instead.


## Usage

Once setup, `cd` into a directory you would like to monitor for changes and start the server by running `assetreload`.

There are optional arguments:

* `path` defines the directory to monitor (defaults to current directory)
* `port` the port on which to start the server (defaults to 8888)

E.g.

	assetreload --path=~/mysite/ --port=8889


### In the browser

Make a copy of `assetreload.js` in your project, and include the following:

	<script src="assetreload.js"></script>
	<script>
		var ar = new AssetReload({
			filesToWatch: ['src/style.css', 'src/script.js'],
			port: 8889
		});
	</script>

Specify all of the files you want to watch using `filesToWatch`. Changes to the current document or JavaScript trigger a page reload, but images and CSS can happen without.

You can automatically generate `assetreload.js` into a directory of your choosing by running:

	assetreload genscript
