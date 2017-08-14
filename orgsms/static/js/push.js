navigator.serviceWorker.register('/push/serviceworker.js').then(function(registration) {
    return registration.pushManager.getSubscription().then(function(subscription) {
        if(subscription) {return subscription;}
        return registration.pushManager.subscribe({ userVisibleOnly: true });
    });
}).then(function(subscription) {
    var rawKey = subscription.getKey ? subscription.getKey('p256dh') : '';
    var key = rawKey ? btoa(String.fromCharCode.apply(null, new Uint8Array(rawKey))) :'';

    var rawAuth = subscription.getKey ? subscription.getKey('auth') : '';
    var auth = rawAuth ? btoa(String.fromCharCode.apply(null, new Uint8Array(rawAuth))) : '';

    var endpoint = subscription.endpoint;
    fetch('/push/register', {
        method: 'post',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({endpoint: subscription.endpoint, key: key, auth: auth})
    }).then((response) => {return response.json();}).then((response) => {
        if(response.success) {
            console.log("Successfully registered", response);
        } else {
            console.error("Registration failed!", response);
        }
    }).catch((e) => {
        console.error("Registration failed!", e.stack || e);
    });
});
