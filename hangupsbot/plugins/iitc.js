// casperjs --web-security=false --ignore-ssl-errors=true --verbose --cookies-file=casperjs.cookie t2.js


var casper = require('casper').create({
    verbose: true,
    logLevel: 'debug',
});

casper.start();
casper.page.settings.resourceTimeout = 62 * 1000;
casper.options.retryTimeout = 2000;
casper.options.waitTimeout = 1 * 60 * 1000;
casper.viewport(1024, 768);

casper.on('remote.message', function (message) {
    this.echo(message);
});


casper.thenOpen('https://ingress.com/intel');
casper.thenBypassUnless(function () {
    var needSignIn = this.evaluate(function () {
        return __utils__.getElementByXPath('.//a[starts-with(.,"Sign in")]');
    });
    return needSignIn;
}, 2);

// Sign In
casper.thenOpen('https://www.google.com/accounts/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttps://www.ingress.com/intel&ltmpl=', function () {
    this.sendKeys("#Email", "____EMAIL____@gmail.com");
    this.sendKeys("#Passwd", "PASSWORD");
    this.click("#signIn");
});
casper.waitForUrl(/https:\/\/www\.ingress\.com\/intel/);

// Inject IITC
casper.then(function _injectIITC() {
    casper.echo("inject to:" + casper.getCurrentUrl());
    casper.evaluate(function () {
        var head = document.getElementsByTagName('head')[0];
        
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://secure.jonatkins.com/iitc/test/total-conversion-build.user.js';
        head.appendChild(script);
        
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://secure.jonatkins.com/iitc/test/plugins/privacy-view.user.js';
        head.appendChild(script);
        
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://secure.jonatkins.com/iitc/test/plugins/portal-highlighter-high-level.user.js';
        head.appendChild(script);
        
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://secure.jonatkins.com/iitc/test/plugins/portal-level-numbers.user.js';
        head.appendChild(script);
    });
    casper.echo("injected");
});

// Wait for IITC Loaded
casper.waitFor(function checkIITCLoaded() {
    var iitcLoaded = this.evaluate(function () {
        return window.iitcLoaded;
    });
    return iitcLoaded;
});

// Google Road Layer, Portal Levels, Hide sidebar
casper.then(function setIITCOption() {
    this.evaluate(function () {
        var baseLayers = window.layerChooser.getLayers().baseLayers;
        for (var l in baseLayers) {
            if (baseLayers[l].name == 'MapQuest OSM') {
                window.layerChooser.showLayer(baseLayers[l].layerId);
                break;
            }
        }

        var overlayLayers = window.layerChooser.getLayers().overlayLayers;
        for (var l in overlayLayers) {
            if (overlayLayers[l].name == 'Portal Levels') {
                window.layerChooser.showLayer(overlayLayers[l].layerId);
                break;
            }
        }
        for (var l in overlayLayers) {
            if (overlayLayers[l].name == 'DEBUG Data Tiles') {
                window.layerChooser.showLayer(overlayLayers[l].layerId, false);
                break;
            }
        }

        var sidebar = $('#scrollwrapper');
        if (sidebar.is(':visible'))
            $('#sidebartoggle').click();
    });
});


function checkStatus() {
    var mapLoaded = casper.page.evaluate(function () {
        var status = window.mapDataRequest.getStatus();
        console.log(status.long + " / " + status.short + " / " + Math.floor(status.progress * 100) + '%');
        return status.short == 'done' || status.short == 'errors' || status.short == 'idle';
    });
    return mapLoaded;
}

var queue = [];
var loading = false;

function capture(options) {
    queue.push(options);

    if (loading) return;
    loading = true;

    setTimeout(processQueue, 100);
}

function processQueue() {
    var cur = queue.shift();
    if (!cur) {
        loading = false;
        return;
    }

    casper.page.evaluate(function (cur) {
        console.log(JSON.stringify(cur));
        window.idleReset();
        window.map.setView(cur.latlng, cur.zoom);
        window.mapDataRequest.refresh();
    }, cur);

    var step = 0;
    var interval = setInterval(function _check(self) {
        if (checkStatus() || ++step > 60) {
            clearInterval(interval);

            casper.echo(JSON.stringify(cur));
            var png = casper.captureBase64('png');
            casper.capture('public_html/aaa.png');

            casper.page.evaluate(function (cur, png) {
                var res = __utils__.sendAJAX(cur.callback, 'POST',
                    JSON.stringify({
                        png: png,
                        echo: cur.name
                    }), false, {
                        contentType: 'application/json'
                    });
                console.log(JSON.stringify(res));
            }, cur, png);

            processQueue();
        } else {
            casper.echo("wait " + step);
        }
    }, 2000);
}

casper.run(function () {
    var server = require('webserver').create();

    service = server.listen(31337, function (request, response) {
        try {
            console.log('Request at ' + new Date());
            console.log(JSON.stringify(request, null, 4));

            var postRaw = (request.postRaw || request.post) + "";
            var data = JSON.parse(postRaw);

            capture(data);

            response.statusCode = 200;
            response.headers = {
                'Cache': 'no-cache',
                'Content-Type': 'text/plain'
            };
            response.write(queue.length);
            response.close();
        } catch (e) {
            casper.echo(""+e);
            response.statusCode = 500;
            response.write(""+e);
            response.close();
        }
    });
});