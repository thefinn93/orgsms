self.addEventListener('push', function(event) {
    var notification;
    if(!event.data) {
        notification = self.registration.showNotification("OrgSMS Is Acting Up!", {"body": "Sorry i have no idea why this happened"})
    } else {
        var payload = event.data.json();
        var title = "Text from " + payload.message.remote_number;
        var body = payload.message.mms ? "" : payload.message.text;
        notification = self.registration.showNotification(title, {body: body});
    }
    event.waitUntil(notification);
});
