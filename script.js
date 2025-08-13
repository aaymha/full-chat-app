const connection = new WebSocket("ws://6.tcp.eu.ngrok.io:14263")

let nickname = prompt("Enter your name: ")
setTimeout(() => {
  connection.send(nickname);
}, 1000);

function send() {
        connection.send(`${nickname}:  ${document.getElementById("message").value}`);
        document.getElementById("message").value = '';
}

document.getElementById("message").onkeydown = function (e) {
    if(e.key === 'Enter') {
        connection.send(`${nickname}:  ${document.getElementById("message").value}`);
        document.getElementById("message").value = '';
    }
}

const div = document.getElementById("content")
div.style.whiteSpace = 'pre-wrap';
connection.onmessage = function (event) { div.append(event.data + '\n')}
