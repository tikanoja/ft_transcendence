const socket = new WebSocket('wss://' + window.location.host + '/ws/app/');
const chatLog = document.getElementById("chat-log");
const inputField = document.getElementById("chat-input");
const submitButton = document.getElementById("chat-submit");

const logMessageCountMax = 32;

socket.onerror   = (event) => { console.log('Chat connection error: ', event); };
socket.onopen    = (event) => { console.log('Chat connection opened', event); };
socket.onclose   = (event) => { console.log('Chat connection closed:', event) };
socket.onmessage = (event) => {
    try {
        const content = JSON.parse(event.data);
        switch (content.type) {
            case "chat.broadcast":
            case "chat.whisper"  : appendMessage(content.sender, content.message); break;
            case "chat.error"    : appendMessage("System", content.message); break;
            default: console.log("Unknown chat event");
        }
    } catch {
        console.log("Invalid event");
    }
};

function appendMessage(source, message) {
    if ([...message].length == 0) {return;}

    const element = document.createElement("div");

    element.classList.add("chat-message");
    element.innerHTML = "[" + source + "] " + message;

    if (chatLog.childElementCount + 1 > logMessageCountMax) {
        chatLog.firstChild.remove();
    }

    chatLog.append(element);
    chatLog.lastChild.scrollIntoView();
}

inputField.addEventListener("keydown", (event) => {
    if (document.activeElement === inputField && event.key == "Enter") {
        submitButton.onclick();
        event.preventDefault();
    }
});

submitButton.onclick = () => {
    if (!inputField.value || socket.readyState != WebSocket.OPEN) {
        return;
    }

    let event;

    if (inputField.value.startsWith("/")) {
        const parts = inputField.value.split(/(\w+)\s+(.*)/)

        if (!parts) {
            return;
        }

        console.log("First pass: ", parts);

        const [ , command, rest, ] = parts;

        switch (command) {
            case "w":
            case "whisper":
                const args = rest.split(/\s+(.*)/);
                console.log(args);
                if (args.length < 3) {
                    appendMessage(chatLog, "System", "Invalid command arguments")
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
                appendMessage(chatLog, "System",
                    "\n" +
                    "/h(elp) - Display chat commands.\n" +
                    "/w(hisper) [username] [message] - Send a direct message.\n"
                );
                return;
        };
    } else {
        event = {
            type : "chat.broadcast",
            message : inputField.value
        };
    }

    try {
        socket.send(JSON.stringify(event));
    } catch {
        console.log("Chat socket not open for sending");
    }

    inputField.value = '';
};
