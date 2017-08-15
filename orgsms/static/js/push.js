function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

navigator.serviceWorker.register('/serviceworker.js').then(function(registration) {
    return registration.pushManager.getSubscription().then(function(subscription) {
        if(subscription) {return subscription;}
        return registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlB64ToUint8Array(applicationServerKey)
        });
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
        credentials: "include",
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
