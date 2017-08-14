self.addEventListener('push', function(event) {
    var notification;
    if(!event.data) {
        notification = self.registration.showNotification("OrgSMS Is Acting Up!", {"body": "Sorry i have no idea why this happened"})
    } else {
        var payload = event.data.json();
        var title = "Text from " + payload.message.remote_number;
        var options = {
            requireInteraction: true,
            tag: "orgsms-message-" + payload.message.id
        };

        if(payload.message.mms) {
            options.image = payload.message.attachment.static_path;
        } else {
            options.body = payload.message.text;
        }
        console.log('Displaying notification', title, options);
        notification = self.registration.showNotification(title, options);
    }
    console.log(notification);
    event.waitUntil(notification);
});
