// PyWebView JS API Bridge
window.pywebview = {
    _callbacks: {},
    _callId: 0,
    
    // Call a Python function
    api: function(funcName, ...args) {
        const callId = this._callId++;
        
        return new Promise((resolve, reject) => {
            // Store the callback for when Python responds
            this._callbacks[callId] = { resolve, reject };
            
            // Call the Python function via the bridge
            window.external.invoke(JSON.stringify({
                func: funcName,
                callId: callId,
                args: args
            }));
        });
    },
    
    // Handle response from Python (called by the C# bridge)
    _handleResponse: function(response) {
        const data = JSON.parse(response);
        const callback = this._callbacks[data.callId];
        
        if (callback) {
            if (data.error) {
                callback.reject(data.error);
            } else {
                callback.resolve(data.result);
            }
            
            // Clean up the callback
            delete this._callbacks[data.callId];
        }
    }
};

// Notify when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Notify Python that DOM is ready
    if (window.pywebview) {
        window.pywebview.api('dom_loaded');
    }
});
