function notificationClick(event) {
    var url = event.notification.data.url;
    console.log('Opening or focusing', url);
    event.notification.close();
    self.clients.claim().then(function() {
        return clients.matchAll({type: 'window'});
    }).then(function(allclients) {
        console.log('Searching for existing window among', allclients);
        for(i = 0; i < allclients.length; i++) {
            if(allclients[i].url === url) {
                allclients[i].focus();
                console.log('Focusing', allclients[i]);
                return allclients[i];
            }
        }
        console.log('No clients found, opening a new window');
    }).then(function(client) {
        if(client) {return client;}
        return clients.openWindow(url).then(function(windowClient) {
            console.log('Opened', windowClient);
            return windowClient;
        });
    }).catch((e) => {console.error(e);});
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
