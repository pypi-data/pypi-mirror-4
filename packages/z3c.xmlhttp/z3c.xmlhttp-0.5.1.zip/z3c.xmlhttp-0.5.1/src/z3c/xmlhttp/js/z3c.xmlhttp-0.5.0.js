//----------------------------------------------------------------------------
/** 
 * @fileoverview Cross browser XMLHttpRequest implementation
 * Make sure the response set the Header to 'no-cache'. 
 *
 * @author Roger Ineichen dev at projekt01 dot ch
 * @version Draft, not complete documented 
 */
//----------------------------------------------------------------------------

//----------------------------------------------------------------------------
// public API
//----------------------------------------------------------------------------

/**
 * Construct a new XMLHttp.
 * @class This is the basic XMLHttp class.
 * @constructor
 * @param {string} url URL pointing to the server
 * @return A new XMLHttp
 */
function XMLHttp(url) {
    this.url = url;
    this.method = 'GET';
    this.async = false;
    this.username = null;
    this.password = null;
    this.timeout = null;
    this.argString = "";
    this.parameters = new Array();
    this.headers = new Array();
    this.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    /* internal status flags */
    this.isAborted = false;
    this.isLoading = false;
    this.isLoaded = false;
    this.isInteractive = false;
    this.isComplete = false;

    /* event handlers (attached functions get called if readyState reached) */
    this.onLoading = null;       // if readyState 1
    this.onLoaded = null;        // if readyState 2
    this.onInteractive = null;   // if readyState 3
    this.onComplete = null;      // if readyState 4
    this.onError = null;         // if readyState 4 and status != 200
    this.onTimeout = null;       // if timeout reached
    this.callback = null;        // if readyState 4 and status == 200
    this.callbackArgs = null;

    /*  response variables */
    this.responseText = null;
    this.responseXML = null;

    /* setup the xmlhttp request now */
    this.xmlhttp = getXmlHttpRequest()
}

/**
 * Set the header information for the XMLHttp instance.
 * @param {array} args of key, value
 */
XMLHttp.prototype.setHeaders = function(args) {
    for (var i in args) {
        this.headers[i] = args[i];
    }
}

/**
 * Set the arguments for the request or the XMLHttp instance.
 * @param {array} args of key, value
 */
XMLHttp.prototype.setArguments = function(args) {
    for (var i in args) {
        // set parameter to the xmlhttp instance or to the parameter array
        if (typeof(this[i])=="undefined") {
            this.parameters[i] = args[i];
        }
        else {
            this[i] = args[i];
        }
    }
}

/**
 * Process a 'POST' request.
 * @param {function} callback callback funtion
 * @param {array} callbackArgs callback arguments
 */
XMLHttp.prototype.post = function(callback, callbackArgs) {
    this.method = 'POST';
    this.async = false;
    if (typeof(callback)=="function") {
        this.callback = callback;
        this.async = true
    }
    if (typeof(callbackArgs)!="undefined") {
        this.callbackArgs = callbackArgs;
    }
    if (this.async) {
        this.process();
    }
    else {
        return this.process();
    }
}

/**
 * Process a 'GET' request.
 * @param {function} callback callback funtion
 * @param {array} callbackArgs callback arguments
 */
XMLHttp.prototype.get = function(callback, callbackArgs) {
    this.method = 'GET';
    this.async = false;
    if (typeof(callback)=="function") {
        this.callback = callback;
        this.async = true
    }
    if (typeof(callbackArgs)!="undefined") {
        this.callbackArgs = callbackArgs;
    }
    if (this.async) {
        this.process();
    }
    else {
        return this.process();
    }
}


//----------------------------------------------------------------------------
// helper methods (can be used directly if you need enhanced access, but the 
// method post and get are the prefered methods for processing a request.) 
//----------------------------------------------------------------------------

/** @private */
XMLHttp.prototype.process = function() {

    if (!this.xmlhttp) return false;

    var self = this;
    this.xmlhttp.onreadystatechange = function() {
        if (self.xmlhttp == null) { return; }
        if (self.xmlhttp.readyState == 1) { self._doLoading(self); }
        if (self.xmlhttp.readyState == 2) { self._doLoaded(self); }
        if (self.xmlhttp.readyState == 3) { self._doInteractive(self); }
        if (self.xmlhttp.readyState == 4) { self._doComplete(self); }
    };

    try {
        var args = null;
        for ( var i = 0; i < this.parameters.length; i++ ) {
            if (this.argString.length>0) {
                this.argString += "&";
            }
            this.argString += encodeURIComponent(i) + "=" + encodeURIComponent(this.parameters[i]);
        }
        if (this.method == "GET") {
            if (this.argString.length>0) {
                this.url += ((this.url.indexOf("?")>-1)?"&":"?") + this.argString;
            }
            this.xmlhttp.open(this.method, this.url, this.async);
        }
        if (this.method == "POST") {
            this.xmlhttp.open(this.method, this.url, this.async, this.username, this.password);
            args = this.argString;
        }
        if (typeof(this.xmlhttp.setRequestHeader)!="undefined" && this.xmlhttp.readyState == 1) {
            for (var i in this.headers) {
                this.xmlhttp.setRequestHeader(i, this.headers[i]);
            }
        }
        if (this.timeout > 0) {
            setTimeout(this._doTimeout, this.timeout);
        }
        this.xmlhttp.send(args);
    }
    catch(z) { return false; }
    /* on async call we return false and on sync calls we return the xmlhttp request */
    if (this.async) {
        return false;
    }
    else {
        return this.xmlhttp;
    }
}


//----------------------------------------------------------------------------
// helper methods (can be used as a standalone cross browser xmlhttp request)
//----------------------------------------------------------------------------

/**
 * Global helper function for a cross browser XMLHttpRequest object.
 * @class This is a global helper function for a cross browser XMLHttpRequest object.
 * @constructor 
 * @return A XMLHttpRequest instance for gecko browsers and a ActiveXObjecct
 * for ie browsers. Unsuported browsers get null returned.
 */
getXmlHttpRequest = function() {
    if (window.XMLHttpRequest) {
        var req = new XMLHttpRequest();
        // some older versions of Moz did not support the readyState property
        // and the onreadystate event so we patch it!
        if (req.readyState == null) {
            req.readyState = 1;
            req.addEventListener("load", function () {
                req.readyState = 4;
                if (typeof req.onreadystatechange == "function") {
                    req.onreadystatechange();
                }
            }, false);
        }
        return req;
    }
    // see comments about the MSXML2.XMLHTTP order,
    // http://blogs.msdn.com/b/xmlteam/archive/2006/10/23/
    // using-the-right-version-of-msxml-in-internet-explorer.aspx
    else if (window.ActiveXObject) {
        var MSXML_XMLHTTP_IDS = new Array(
            "MSXML2.XMLHTTP.6.0",
            "MSXML2.XMLHTTP.3.0",
            "MSXML2.XMLHTTP",
            "MSXML2.XMLHTTP.5.0",
            "MSXML2.XMLHTTP.4.0",
            "Microsoft.XMLHTTP");
        var success = false;
        for (var i = 0; i < MSXML_XMLHTTP_IDS.length && !success; i++) {
            try {
                return new ActiveXObject(MSXML_XMLHTTP_IDS[i]);
                success = true;
            } catch (e) {}
        }
    }
    else {
        return null;
    }
}


//----------------------------------------------------------------------------
// built in helper methods
//----------------------------------------------------------------------------

/** @private */
XMLHttp.prototype._doLoading = function(self) {
    if (self.isLoading) { return; }
    if (typeof(self.onLoading)=="function") {
        self.onLoading(self.xmlhttp);
        }
    self.isLoading = true;
}

/** @private */
XMLHttp.prototype._doLoaded = function(self) {
    if (self.isLoaded) { return; }
    if (typeof(self.onLoaded)=="function") {
        self.onLoaded(self.xmlhttp);
    }
    self.isLoaded = true;
}

/** @private */
XMLHttp.prototype._doInteractive = function(self) {
    if (self.isInteractive) { return; }
    if (typeof(self.onInteractive)=="function") {
        self.onInteractive(self.xmlhttp);
    }
    self.isInteractive = true;
}

/** @private */
XMLHttp.prototype._doComplete = function(self) {
    if (self.isComplete || self.isAborted) { return; }
    self.isComplete = true;
    self.status = self.xmlhttp.status;
    self.statusText = self.xmlhttp.statusText;
    self.responseText = self.xmlhttp.responseText;
    self.responseXML = self.xmlhttp.responseXML;
    if (typeof(self.onComplete)=="function") {
        self.onComplete(self.xmlhttp);
    }
    if (self.xmlhttp.status==200 && typeof(self.callback)=="function") {
        if (self.callbackArgs) {
            self.callback(self.xmlhttp, self.callbackArgs);
        }
        else {
            self.callback(self.xmlhttp);
        }
    }
    if (self.xmlhttp.status!=200 && typeof(self.onError)=="function") {
        self.onError(self.xmlhttp);
    }
    if (self.async) {
        // on async calls, clean up so IE doesn't leak memory
        delete self.xmlhttp['onreadystatechange'];
        self.xmlhttp = null;
    }
}

/** @private */
XMLHttp.prototype._doTimeout = function(self) {
    if (self.xmlhttp!=null && !self.isComplete) {
        self.xmlhttp.abort();
        self.isAborted = true;
        if (typeof(self.onTimeout)=="function") {
            self.onTimeout(self.xmlhttp);
        }
    // Opera won't fire onreadystatechange after abort, but other browsers do. 
    // So we can't rely on the onreadystate function getting called. 
    // Clean up here!
    delete self.xmlhttp['onreadystatechange'];
    self.xmlhttp = null;
    }
}
