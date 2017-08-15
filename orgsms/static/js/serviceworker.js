function notificationClick(event) {
    var url = self.origin + event.notification.data.url;
    console.log('Opening or focusing', url);
    var windowPromise = self.clients.matchAll().then(function(clientList) {
        console.log('Searching for existing window among', clientList);
        for(var i = 0; i < clientList.length; i++) {
            var client = clientList[i];
            if(client.url === url) {
                console.log('Focusing', client);
                return client.focus();
            }
        }
        console.log('No clients found, opening a new window');
    }).then(function(client) {
        if(!client) {
            console.log('No client found with url =', url, '- opening new window');
            self.clients.openWindow(event.notification.data.url)
        };
    }).catch((e) => {console.error(e);});
    event.waitUntil(windowPromise);
}


function push(event) {
    var notification;
    console.log("Received push event", event);
    if(!event.data) {
        notification = self.registration.showNotification("OrgSMS Is Acting Up!", {"body": "Sorry i have no idea why this happened"})
    } else {
        var payload = event.data.json();
        var title = "Text from " + payload.message.remote_number;
        var options = {
            requireInteraction: true,
            tag: "orgsms-message-" + payload.message.id,
            data: {
                url: payload.message.url
            }
        };

        if(payload.message.mms) {
            options.image = payload.message.attachment.static_path;
        } else {
            options.body = payload.message.text;
        }
        console.log('Displaying notification', title, options);
        notification = self.registration.showNotification(title, options);
    }
    event.waitUntil(notification);
}

self.addEventListener('notificationclick', notificationClick);
self.addEventListener('push', push);

self.addEventListener('install', function(event) {
    event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', function(event) {
    event.waitUntil(self.clients.claim());
});
