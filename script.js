const connection = new WebSocket(`wss://${window.location.host}/ws`);

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

const div = document.getElementById("display_text")
div.style.whiteSpace = 'pre-wrap';
connection.onmessage = function (event) { div.append(event.data + '\n')}