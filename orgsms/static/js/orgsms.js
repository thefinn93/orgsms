function livestamp(elements) {
    if(elements === undefined) {
      elements = document.querySelectorAll('[data-livestamp]');
    }
    for(var i = 0; i < elements.length; i++) {
        elements[i].innerText = moment(parseFloat(elements[i].dataset.livestamp)*1000).fromNow();
    }
}

function newmessage(message) {
  if(message.id) {
      var candidate = document.querySelector('.msg[data-id="' + message.id + '"]');
      console.log("maybe re-rendering message", message.id, candidate);
      if(candidate) {
        return candidate;
      }
  }
  if(message.source_session == socket.id) {
      console.log('Not rendering message that appears to come from us:', message);
      return false;
  }
  var msg = document.createElement('div');
  msg.classList.add('msg', message.inbound ? 'inbound' : 'outbound');

  if(message.id) {
      msg.dataset.id = message.id;
  }

  var top = document.createElement('div');
  top.classList.add('msg-top');
  top.innerText = message.inbound ? message.remote_number : "Me";
  msg.appendChild(top);

  var img = document.createElement('img');
  img.src = "https://via.placeholder.com/50x50";
  img.classList.add('circle', 'contact-photo');
  msg.appendChild(img);

  var textbox = document.createElement('div');
  textbox.classList.add('msg-text');
  textbox.innerText = message.text;
  msg.appendChild(textbox);

  var timestamp = document.createElement('div');
  timestamp.classList.add('timestamp');
  if(message.timestamp) {
    timestamp.dataset.livestamp = message.timestamp;
    livestamp([timestamp]);
  } else {
    timestamp.classList.add('unsent');
    timestamp.innerText = "...";
  }
  msg.timestamp = timestamp;
  msg.appendChild(timestamp);

  document.querySelector('.msg-thread').appendChild(msg);
  msg.scrollIntoView();
  return msg;
}

function send(text, source, destination) {
    var message = newmessage({text: text, inbound: false});
    var socket_packet = {to: destination, from: source, text: text};
    console.log("Sending packet", socket_packet);
    socket.emit('send', socket_packet, function(status) {
        console.log(status);
        if(status.success) {
            message.timestamp.classList.remove('unsent');
            message.timestamp.dataset.livestamp = status.message.timestamp;
            livestamp([message.timestamp]);
            message.dataset.id = status.message.id;
        } else {
          msg.classList.add('failed');
        }
    });
}

function textboxKeyDown(e) {
    if(e.keyCode == 13 && !e.shiftKey) { // Enter pressed without shift
        e.preventDefault();
        send(this.value, parseInt(this.dataset.from), parseInt(this.dataset.to));
        this.value = "";
        return false;
    }
}

function onExternalMessage(message) {
  console.log(message);
  if(document.querySelector('.msg-thread[data-number="' + message.remote_number + '"]')) {
    newmessage(message);
  }
}

function fakelink() {
  window.location.href = this.dataset.href;
}

var socket = io.connect();


(function() {
    livestamp();
    setInterval(livestamp, 10000); // Re-render all timestamps every 10 seconds

    var lastmsg = document.querySelector(".msg:last-child");
    if(lastmsg) lastmsg.scrollIntoView();

    var textinput = document.querySelector(".textinput");
    if(textinput) textinput.addEventListener('keydown', textboxKeyDown);

    socket.on('newmessage', onExternalMessage);

    var fakelinks = document.querySelectorAll('.fakelink[data-href]');
    for(var i = 0; i < fakelinks.length; i++) {
      fakelinks[i].addEventListener('click', fakelink);
    }
})();
