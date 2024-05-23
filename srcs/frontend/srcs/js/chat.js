import { profileLinkHandler } from "./handlers.js"

let   socket = null;

const chatLog      = document.getElementById("chat-log");
const inputField   = document.getElementById("chat-input");
const submitButton = document.getElementById("chat-submit");

const logMessageCountMax = 32;

const helpMessage = "\n" +
                    "/h - Display chat commands.\n" +
                    "/w [username] message - Send a direct message.\n" +
                    "/b [username] - Block user.\n" +
                    "/u [username] - Unblock user.\n" +
                    "/i [username] [Pong/Color] - Send a game invite.\n";

inputField.onkeydown = (e) => { if (e.key === "Enter") { _submitHandler(); e.preventDefault(); } }

submitButton.onclick = _submitHandler;

document.addEventListener("login" , connect);
document.addEventListener("logout", disconnect);

connect();

function connect() {
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
        socket.onerror   = (event) => { console.log('Chat socket error: ',     event); };
        socket.onclose   = (event) => {
            console.log(event);
            socket = null;
            _set_disabled(true);
            while (chatLog.lastChild) { chatLog.lastChild.remove(); }
        };
        socket.onmessage = _messageHandler;
    }

    _set_disabled(false);
}

function disconnect() {
    if (socket) {
        socket.close()
    }
}

function _submitHandler() {
    inputField.value.trim();

    if (inputField.value == "" || socket.readyState != WebSocket.OPEN) {
        return null;
    }

    try {
        const payload = _parseInput(inputField.value) 

        if (payload) {
            socket.send(JSON.stringify(payload));
        } else {
            _appendMessage( _createSourceElement("System"), helpMessage);
        }

    } catch (e) {
        console.error("Failed to submit chat message: ", e);
    }

    inputField.value = '';
};

function _parseInput(input) {
    if (!input.startsWith("/")) {
        return { type: "chat.broadcast", message: input };
    }

    const parts = input.split(/^\/(\w)\s+/g).filter(s => { return s != ""; });

    if (!parts || parts.length != 2) {
        return null;
    }

    const [ command, rest ] = parts;

    console.log(parts);

    switch (command) {
        case "w": {
            const args = rest.split(/^(\S+)\s+/g).filter(s => { return s != ""; });
            if (args && args.length == 2) {
                return {
                    type: "chat.whisper",
                    receiver: args[0],
                    message: args[1]
                };
            }
            break;
        }

         case "b": {
            const args = rest.trim();
            if (args && /^[A-Za-z0-9]+$/.test(args)) {
                return {
                    type: "chat.block",
                    username: args,
                }
            }
            break;
         }

         case "u": {
            const args = rest.trim();
            if (args && /^[A-Za-z0-9]+$/.test(args)) {
                return {
                    type: "chat.unblock",
                    username: args,
                }
            }
         }

         case "i": {
            const args = rest.split(/^(\S+)\s+/g).filter(s => { return s != ""; });
            if (args && args.length == 2 && /^[A-Za-z0-9]+$/.test(args[0])) {
                args[1] = args[1].toLowerCase();
                if (args[1] == "pong" || args[1] == "color") {
                    return {
                        type: "chat.invite",
                        username: args[0],
                        game: args[1],
                    }
                }
            }
         }

        default: break;
    };
    return null;
}


function _messageHandler(event) {
    try {
        const content = JSON.parse(event.data);
        console.log("content")
        switch (content.type) {
            case "chat.broadcast": // Same fronted behaviour as whisper, difference being indicated would be nice I guess.
            case "chat.whisper"  : _appendMessage( _createUsernameElement(content.sender), content.message ); break;
            case "chat.system"   : _appendMessage( _createSourceElement("System"), content.message ); break;
            case "chat.error"    : _appendMessage( _createSourceElement("Error"),  content.message ); break;

            default: throw Error("Unknown chat event");
        }
    } catch (e) { console.error("Chat message handling failure: ", e); }
}

function _set_disabled(isDisabled) {
    chatLog.disabled      = isDisabled;
    submitButton.disabled = isDisabled;
    inputField.disabled   = isDisabled;
}

function _createUsernameElement(name) {
    const userLink = document.createElement("a");
    userLink.href = "/profile/" + name;
    userLink.append(document.createTextNode(name));
    userLink.addEventListener("click", profileLinkHandler);

    const userLinkBold = document.createElement("b");
    userLinkBold.append(userLink);

    return userLinkBold;
}

function _createSourceElement(name) {
    const element = document.createElement("b");
    element.textContent = name;
    return element
}

function _appendMessage(source, message) {
    if ([...message].length === 0) { return; }

    const container = document.createElement("div");
    container.classList.add("chat-message");
    container.append(source);
    container.append(document.createTextNode("  " + message));

    if (chatLog.childElementCount + 1 > logMessageCountMax) {
        const expiredMessage = chatLog.firstChild;
        expiredMessage.removeEventListener("click", profileLinkHandler);
        expiredMessage.remove();
    }

    chatLog.append(container);
    chatLog.lastChild.scrollIntoView();
}
