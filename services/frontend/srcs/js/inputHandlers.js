

// buttonHandlers.js
export function increaseButtonClickHandler() {
    sendRequest('pong/increase_number/', function (response) {
        console.log('Increased number:', response.number);
    });
}

export function decreaseButtonClickHandler() {
    sendRequest('pong/decrease_number/', function (response) {
        console.log('Decreased number:', response.number);
    });
}
