# Ground station code

Ground station software for glider monitoring (glider_drone)

## Overview

## Installation

#### To hit the server on port 80

* Install Apache2
* Enable apache modules: [proxy, proxy_http, proxy_wstunnel, rewrite]
`sudo a2enmod proxy proxy _http proxy_wstunnel rewrite`
* Create a groundstation site
 ```
 <VirtualHost *:80>
	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/html

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

	RewriteEngine on
	RewriteCond %{HTTP:UPGRADE} ^WebSocket$ [NC]
	RewriteCond %{HTTP:CONNECTION} ^Upgrade$ [NC]
	RewriteRule .* ws://localhost:8000%{REQUEST_URI} [P]

	ProxyPass / http://127.0.0.1:8000/ retry=0
	ProxyPassReverse / http://127.0.0.1:8000/ retry=0
 </VirtualHost>
 ```
 * Enable the site (`apache a2enmod <Site name>`)
## Usage

### Enable telemetry beep on Chrome

If using chrome on mobile, you may need to allow sounds to play automatically

You can do so by putting this in the chrome URL: `chrome://flags/#disable-gesture-requirement-for-media-playback`
 (Thanks to https://stackoverflow.com/a/28812647)