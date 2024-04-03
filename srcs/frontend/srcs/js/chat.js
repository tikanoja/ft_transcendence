const socket = new WebSocket('wss://' + window.location.host + '/ws/app/');

let contentField = document.getElementById("chat-content");
let inputField = document.getElementById("chat-input");

const submitButton = document.getElementById("chat-submit");

const appendMessage = (rootElement, source, message) => {
    if ([...message].length == 0) {return;}

    const messageParagraph = document.createElement("p");
    messageParagraph.innerHTML = "[" + source + "] " + message + "\n";

    rootElement.append(messageParagraph);
}

socket.onerror = (error) => {
    console.log('Chat connection error: ', error);
};

socket.onopen = (event) => {
    console.log('Chat connection opened', event);
};

socket.onclose = (event) => {
    console.log('Chat connection closed:', event)
};

socket.onmessage = (event) => {
    const content = JSON.parse(event.data);

    switch (content.type) {
        case "chat.message":
            appendMessage(contentField, content.source, content.message);
            break;
        case "chat.error":
            appendMessage(contentField, "System", content.message);
            break;
    }
};

inputField.onkeydown = (event) => {
    if (document.activeElement == inputField && event.key == "Enter") {
        submitButton.onclick();
    }
};

submitButton.onclick = () => {
    if (!inputField.value || socket.readyState != WebSocket.OPEN) {
        return;
    }

    let packet = { "type" : "chat.message" };
    if (inputField.value.startsWith("/")){
        const regex_expression = /^\/(\w)\s+(\w+)\s+(.*)$/;
        const parts = inputField.value.match(regex_expression);

        if (!parts)
            return // TODO should print error..

        let [_, command, argument, message] = parts;

        switch (command) {
            case "w":
                packet["receiver"] = argument;
                packet["message"] = message;
                break;
            default:
                console.log("unknown chat command");
                return;
        };

    } else {
        packet["receiver"] = "Global"; // TODO Should be current room of chat client
        packet["message"] = inputField.value;
    }

    console.log("Sending: ", packet);
    socket.send(JSON.stringify(packet));
    inputField.value = '';
};
