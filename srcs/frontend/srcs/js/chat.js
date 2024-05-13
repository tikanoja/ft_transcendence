import { profileLinkHandler, checkLogin } from "./index.js"

let   socket = null;

const chatLog      = document.getElementById("chat-log");
const inputField   = document.getElementById("chat-input");
const submitButton = document.getElementById("chat-submit");

const logMessageCountMax = 32;

document.addEventListener("login" , connect);
document.addEventListener("logout", disconnect);

connect();

function connect() {
    console.log("Chat connecting...");

    if (!socket) {
        console.log("Establishing chat websocket connection...");
        try {
            socket = new WebSocket('wss://' + window.location.host + '/ws/app/');
        } catch (e) {
            console.log("Failed to create chat websocket: ", e);
            socket = null;
            return
        }

        socket.onopen    = (event) => { console.log('Chat connection opened' , event); _set_disabled(false); };

        socket.onerror   = (event) => {
            console.log('Chat socket error: ', event);
        };

        socket.onclose   = (event) => {
            console.log('Chat connection closed:', event);
            _set_disabled(true);
            while (chatLog.lastChild) chatLog.lastChild.remove();
        };

        socket.onmessage = (event) => {
            try {
                const content = JSON.parse(event.data);
                switch (content.type) {
                    case "chat.broadcast":
                    case "chat.whisper"  : _appendMessage(content.sender, content.message); break;
                    case "chat.error"    : _appendMessage("System", content.message); break;
                    default: console.log("Unknown chat event");
                }
            } catch (e) {
                console.log("Event error:", e);
            }
        };
    }

    _set_disabled(false);
}

async function disconnect() {
    console.log("Chat disconnecting...");

    if (socket) {
        await socket.close()
        socket = null;
    }
}

function _set_disabled(isDisabled) {
    chatLog.disabled      = isDisabled;
    submitButton.disabled = isDisabled;
    inputField.disabled   = isDisabled;
}

function _appendMessage(source, message) {
    if ([...message].length === 0) { return; }

    const userLink = document.createElement("a");
    userLink.href = "/profile/" + source;
    userLink.append(document.createTextNode(source));
    userLink.addEventListener("click", profileLinkHandler);

    const userLinkBold = document.createElement("b");
    userLinkBold.append(userLink);

    const container = document.createElement("div");
    container.classList.add("chat-message");
    container.append(userLinkBold);
    container.append(document.createTextNode("  " + message));

    if (chatLog.childElementCount + 1 > logMessageCountMax) {
        const expiredMessage = chatLog.firstChild;
        expiredMessage.removeEventListener("click", profileLinkHandler);
        expiredMessage.remove();
    }

    chatLog.append(container);
    chatLog.lastChild.scrollIntoView();
}

inputField.addEventListener("keydown", (event) => {
    if (document.activeElement === inputField && event.key === "Enter") {
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

        const [ , command, rest, ] = parts;

        switch (command) {
            case "w":
            case "whisper":
                const args = rest.split(/\s+(.*)/);
                console.log(args);
                if (args.length < 3) {
                    _appendMessage("System", "Invalid command arguments")
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
                _appendMessage("System",
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
        console.log("Chat socket not open");
    }

    inputField.value = '';
};
