//-----------------------------------------------------------------------------
// JSON-RPC content loader and form processor methods
/*

Usage:

register callback handler:

  function doitFunction(response){
      alert(response.content);
  }
  j01RegisterCallback('doit', doitFunction);
  

without event delegation:

  $('a.click').j01LoadContent({'callbackName': 'doit'})

with event delegation:

  $('document').j01LoadContentOn('hoover', 'a.load', {'callbackName': 'doit'})

  $('#content').j01LoadContentOnClick('a.loadOnClick', {'callbackName': 'doit'})

or enhance the J01ContentLoader with prototype and use the new method:

  J01ContentLoader.prototype.update = function(self) {
      // fade out, load content, fade in
  };
  var loader = new J01ContentLoader({'callbackName': 'doit'});
  loader.update('foo bar');


General setup:

  global setup during loading the script
    1. setup a callback handler registry
    3. setup statechange handler if global History.enabled

  optional setup in your project scripts
    1. implement custom callback method if not default j01RenderContent is used
    2. register custom callback

You can setup links without history support with:

  $('#foo').j01LoadContent({'enableHistory': false})

  link setup
    1. apply j01LoadContentProcessor click handler to links

  on click
    1. get url from link element (this)
    2. get callback from registry by callbackName
    3. call j01LoadContentProcessor with url and callback
    4. render response with callback method (asynchron)
    5. render content based on contentTargetExpression or default
    6. process error if any with built-in error handler in callback

You can setup links with history support (default) like:

  $('#foo').j01LoadContent()

  link setup
    1. apply notifyClick click handler to links

  on click
    1. get url from link element (this)
    2. add j=1 param to url (mark as j01LoadContent state url)
    3. optional add callbackName as 'c' param to url
    4. setup state with url
    5. call History.pushState which will notify statechange

  on statechange (this get called on any statechange)
    1. get state
    2. check 'j' param (condition for our state processing)
    3. get callback method based on 'c' param if state is for us
    4. call j01LoadContentProcessor with url, callback
    5. remove j, c params from url
    6. process response with callback method (asynchron)
    7. render content based on contentTargetExpression or default
    8. process error if any with built-in error handler in callback

*/
//-----------------------------------------------------------------------------

// callback registry
var j01CallbackRegistry = []; // new Array();
var j01HTMLBody = $('html, body');

// generic error handling
function j01RenderContentError(response) {
    // error handling
    if (response.data.nextURL) {
        window.location.href = response.data.nextURL;
    } else if (response.data.i18nMessage){
        alert(response.data.i18nMessage); // p01.checker.silence
    }else {
        alert(response.message); // p01.checker.silence
    }
}

function j01RenderScrollToProcessing(response, targetContainer) {
    // process scrollTo
    if (response.scrollToExpression) {
        scrollContainer = $(response.scrollToExpression);
        // get previous height
        var wHeight = $(window).height();
        var sOffset = scrollContainer.offset();
        if (scrollContainer && sOffset) {
            var scrollTop = sOffset.top;
            if (response.scrollToOffset) {
                scrollTop += response.scrollToOffset;
            }
            if (scrollTop >= wHeight) {
                if (response.scrollToSpeed) {
                    scrollToSpeed = response.scrollToSpeed
                } else {
                    scrollToSpeed = 500;
                }
                // scroll, but only if outside viewport and only the missing
                // height
                scrollTop -= wHeight;
                j01HTMLBody.animate({'scrollTop': scrollTop}, scrollToSpeed);
            }
        }
    }
}

// generic success handling
function j01RenderContentSuccess(response, contentTargetExpression) {
    if (response.nextURL) {
        window.location.href = response.nextURL;
    } else {
        // success handling
        var targetContainer;
        if (response.contentTargetExpression) {
            targetContainer = $(response.contentTargetExpression);
        } else {
            targetContainer = $(contentTargetExpression);
        }
        // implement animations
        targetContainer.empty();
        targetContainer.html(response.content);
        // process scrollTo
        j01RenderScrollToProcessing(response, targetContainer)
        // nextHash is supported in response but not implemented in callback yet
    }
}

// generic response processor
function j01RenderContent(response) {
    if (response.code) {
        // error handling
        j01RenderContentError(response);
    } else {
        // success handling with default content target expression
        j01RenderContentSuccess(response, '#content');
    }
}

function j01RegisterCallback(callbackName, callback) {
    // register callback by name
    if (callbackName !== 'j01RenderContent') {
        var key;
        for (key in j01CallbackRegistry) {
            if (key === callbackName) {
                // callback already registered
                // TODO: prevent problems by check if the same callbackName is 
                //       registered with a different function
                return false;
            }
        }
        // add callback
        j01CallbackRegistry[callbackName] = callback;
    }
    return true;
}

function j01GetCallback(callbackName) {
    // get callback by name
    if (callbackName) {
        var key;
        for (key in j01CallbackRegistry) {
            if (key === callbackName) {
                // return this callback method
                return j01CallbackRegistry[callbackName];
            }
        }
    }
    // return default callback
    return j01RenderContent;
}

// url and form helpers
function j01RemoveURLParam(url, param) {
    var urlparts = url.split('?'),
        prefix,
        pars,
        i;
    if (urlparts.length >= 2) {
        prefix = encodeURIComponent(param) + '=';
        pars = urlparts[1].split(/[&;]/g);
        for (i = 0; i < pars.length; i = i + 1) {
            if (pars[i].indexOf(prefix, 0) === 0) {
                pars.splice(i, 1);
            }
        }
        if (pars.length > 0) {
            return urlparts[0] + '?' + pars.join('&');
        } else {
            return urlparts[0];
        }
    } else {
        return url;
    }
}

function j01URLToArray(url, params) {
    if (typeof params === "undefined") {
        params = {};
    }
    var qString = null,
        strQueryString,
        i;
    if (url.indexOf("?") > -1) {
        strQueryString = url.substr(url.indexOf("?") + 1);
        qString = strQueryString.split("&");
    }
    if (qString === null) {
        if (typeof params !== "undefined") {
            return params;
        }else{
            return null;
        }
    }
    for (i = 0; i < qString.length; i = i + 1) {
        params[qString[i].split("=")[0]] = qString[i].split("=")[1];
    }
    return params;
}

// generic content loader which is able to load content from server via jsonrpc
function j01LoadContentProcessor(url, callback) {
    // remove internal j and c params e.g. ?j=1 or &j=1 but keep ? if more
    // params given
    if (url.indexOf("?") > -1) {
        url = j01RemoveURLParam(url, 'j');
        url = j01RemoveURLParam(url, 'c');
    }
    var requestId = 'j01LoadContent',
        params;
    proxy = getJSONRPCProxy(url);
    proxy.addMethod('j01LoadContent', callback, requestId);
    params = j01URLToArray(url);
    if (params) {
        proxy.j01LoadContent(params);
    } else {
        proxy.j01LoadContent();
    }
}

// setup history support based on statechange event handler
(function(window, undefined) {
    // condition
    var History = window.History;
    if (!History || !History.enabled) {
        return false;
    }
    // bind to statechange event
    History.Adapter.bind(window, 'statechange', function () {
        // get the last saved state (current)
        var State = History.getState(),
            url = State.url,
            params = j01URLToArray(url),
            callback;
        State = History.getState();
        if (params && params.j) {
            // marked as j01LoadContent call, get callback now
            callback = j01GetCallback(params.c);
            j01LoadContentProcessor(url, callback);
        }
    });
})(window);

// J01ContentLoader
var J01ContentLoader = function (settings) {
    var t,
        History;
    this.settings = $.extend({
        callbackName: 'j01RenderContent',
        contentTargetExpression: null,
        requestId: null,
        handleError: null,
        preCallFunction: null,
        enableHistory: true
    }, settings);

    if (typeof this.settings.callbackName !== "string") {
        t = typeof this.settings.callbackName;
        alert("j01LoadContent: callbackName must be a string not " + t); // p01.checker.silence
    }
    this.enableHistory = false;
    History = window.History;
    if (this.settings.enableHistory && History.enabled) {
        this.enableHistory = true;
    }
};

J01ContentLoader.prototype.loadContent = function (self) {
    // load content from server via jsonrpc
    var url = $(self).attr('href'),
        callback = j01GetCallback(this.settings.callbackName);
    j01LoadContentProcessor(url, callback);
};

J01ContentLoader.prototype.notifyClick = function (self) {
    var url = $(self).attr('href'),
        History = window.History;
    // let's add 'j' as a j01LoadContent call marker 
    if (!/\?/.test(url)) {
        url += '?';
    } else {
        url += '&';
    }
    url += 'j=1';
    if (this.settings.callbackName !== 'j01RenderContent') {
        url = url + '&c=' + this.settings.callbackName;
    }
    // XXX: Don't use data and title which allows to bookmark links otherwise
    // with data and title we will get the _suid which we can't handle
    // given from bookmark. This means if _usid is used, we can't reset the
    // state.
    
    // why do we use data? what doesn't work without a data timestamp?
    // Currently we can't force processing the concept with a _suid.
    // Find out why we added data. See comment above, currentyl including data
    // prevents bookmark to work...

    // push state which forces to notify statechange, we use a timestamp
    // which allows to use state change on the same page
    var data = {timestamp: (new Date().getTime())};
    History.pushState(data, null, url);
};

/**
 * j01LoadContent without delegation (not recommended)
 * this plugin does not re bind handlers for new loaded content
 */
(function ($) {
    $.fn.j01LoadContent = function (settings) {
    // setup loader with given settings
        var loader = new J01ContentLoader(settings);
        return this.each(function () {
            // apply event handler to links
            $(this).click(function (event) {
                // process pre call function with context
                if (this.settings.preCallFunction) {
                    this.settings.preCallFunction(this);
                }
                if (loader.enableHistory) {
                    // continue as normal for cmd clicks etc
                    if (event.which === 2 || event.metaKey) {
                        return true;
                    } else {
                        loader.notifyClick(this);
                    }
                } else {
                    loader.loadContent(this);
                }
                event.preventDefault();
                return false;
            });
        });
    };
})(jQuery);

// j01LoadContentOn
(function ($) {
    $.fn.j01LoadContentOn = function (events, selector, settings) {
        // apply delegated event handler
        return this.on(events, selector, function (event) {
            var loader = new J01ContentLoader(settings);
            // process pre call function with context
            if (loader.settings.preCallFunction) {
                loader.settings.preCallFunction(this);
            }
            if (loader.enableHistory) {
                loader.notifyClick(this);
            } else {
                loader.loadContent(this);
            }
            event.preventDefault();
            return false;
        });
    };
})(jQuery);

/**
 * j01LoadContentOnClick uses delegation pattern (recommended)
 * this plugin uses the delegation pattern and works on new loaded content
 */
(function ($) {
    $.fn.j01LoadContentOnClick = function (selector, settings) {
        if (typeof selector === "object") {
            // only settings given, use default selector and adjust settings
            settings = selector;
            selector = 'a.j01LoadContentLink';
        } else if (typeof selector === "undefined") {
            // non argument given, use default selector
            selector = 'a.j01LoadContentLink';
        }
        // apply delegated event handler to click event
        return this.j01LoadContentOn('click', selector, settings);
    };
})(jQuery);

(function ($) {
/**
 * Serializes form data into a 'submittable' string. This method will return a 
 * string in the format: url?name1=value1&amp;name2=value2 or url
 */
    $.fn.j01FormToURL = function (url) {
        //hand off to jQuery.param for proper encoding
        var query = this.serialize();
        if (query) {
            return url +'?'+ query;
        } else {
            return url;
        }
    };

/**
 * Taken from jquery.form and modified. We use an object instead of an array as
 * data container. This makes it possible to use the data with JSON-RPC.
 * 
 * j01FormToArray() gathers form element data into a data object which is a 
 * collection of objects. Each object in the data object provides the field
 * name and the value. An example of an array for a simple login form might be:
 * {'login': 'jresig', 'password': 'secret'}
 */
    $.fn.j01FormToArray = function (handlerName) {
        var data = {},
            form,
            els,
            i,
            max,
            el,
            n,
            v,
            j,
            jmax,
            inputs,
            input;
        function add(n, v) {
            if (v !== null && typeof v !== 'undefined') {
                if (data[n]) {
                    var val = data[n];
                    if (val && val.constructor === Array) {
                        val.push(v);
                    } else {
                        val = [data[n]];
                        val.push(v);
                    }
                    data[n] = val;
                    
                } else {
                    data[n] = v;
                }
            }
        }
        if (this.length === 0) {
            return data;
        }

        form = this[0];
        els = form.elements;
        if (!els) {
            return data;
        }
        for (i = 0, max = els.length; i < max; i = i + 1) {
            el = els[i];
            n = el.name;
            if (!n) {
                continue;
            }

            v = $.j01FieldValue(el);
            if (v && v.constructor === Array) {
                for (j = 0, jmax = v.length; j < jmax; j = j + 1) {
                    add(n, v[j]);
                }
            } else {
                if (v !== null && typeof v !== 'undefined') {
                    add(n, v);
                }
            }
        }

        if (form.clk) {
            // input type=='image' are not found in elements array! handle them here
            inputs = form.getElementsByTagName("input");
            for (i = 0, max = inputs.length; i < max; i = i + 1) {
                input = inputs[i];
                n = input.name;
                if (n && !input.disabled && input.type === "image" && form.clk === input) {
                    add(n + '.x', form.clk_x);
                    add(n + '.y', form.clk_y);
                }
            }
        }
        if (handlerName) {
            add('j01FormHandlerName',  handlerName);
        }
        return data;
    };

    $.j01FieldValue = function (el) {
        var n = el.name,
            t = el.type,
            tag = el.tagName.toLowerCase(),
            index,
            a,
            ops,
            one,
            max,
            i,
            op,
            v;

        if (!n || el.disabled || t === 'reset' || t === 'button' ||
                ((t === 'checkbox' || t === 'radio') && !el.checked) ||
                ((t === 'submit' || t === 'image') && el.form && el.form.clk !== el) ||
                (tag === 'select' && el.selectedIndex === -1)) {
            return null;
        }

        if (tag === 'select') {
            index = el.selectedIndex;
            if (index < 0) {
                return null;
            }
            a = [];
            ops = el.options;
            one = (t === 'select-one');
            max = (one ? index + 1 : ops.length);
            for (i = (one ? index : 0); i < max; i = i + 1) {
                op = ops[i];
                if (op.selected) {
                    // extra pain for IE...
                    v = $.browser.msie && !(op.attributes.value.specified) ? op.text : op.value;
                    if (one) {
                        return v;
                    }
                    a.push(v);
                }
            }
            return a;
        }
        return el.value;
    };
})(jQuery);
