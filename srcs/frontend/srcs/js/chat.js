const socket = new WebSocket('wss://' + window.location.host + '/ws/app/');

const log = document.getElementById("chat-log");
const input = document.getElementById("chat-input");

const submitButton = document.getElementById("chat-submit");


function appendMessage(rootElement, source, message) {
    if ([...message].length == 0) {return;}

    const element = document.createElement("div");

    element.classList.add("chat-message")
    element.innerHTML = "[" + source + "] " + message;

    rootElement.append(element);
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

    console.log(content)

    switch (content.type) {
        case "chat.whisper": appendMessage(log, content.sender, content.message); break;
        case "chat.error"  : appendMessage(log, "System", content.message); break;
    }
};

input.onkeydown = (event) => {
    if (document.activeElement == input && event.key == "Enter") {
        submitButton.onclick();
    }
};

submitButton.onclick = () => {
    if (!input.value || socket.readyState != WebSocket.OPEN) {
        return;
    }

    let event;

    if (input.value.startsWith("/")){
        const parts = input.value.match(/^\/(\w)\s+(\w+)\s+(.*)$/);

        if (!parts) {
            return // TODO should print error..
        }

        const [_, command, ...args] = parts;

        console.log(command, args);

        switch (command) {
            case "w":
            case "whisper":
                if (args.length < 2) {
                    appendMessage(log, "System", "Invalid command arguments")
                    return;
                }
                event = {
                    type: "chat.whisper",
                    receiver: args[0],
                    message: args[1]
                };
                break;

            case "h":
            case "help":
            default:
                appendMessage(log, "System",
                    '\n \
                    /h(elp)                         - Display chat commands.\n \
                    /w(hisper) [username] [message] - Send a direct message.\n'
                )
                return;
        };
    } else {
        event = {
            type : "chat.broadcast",
            message : input.value
        };
    }

    try {
        socket.send(JSON.stringify(event));
    } catch {
        console.log("Chat socket not open for sending");
    }

    input.value = '';
};
