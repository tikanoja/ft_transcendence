import { getSingleHandlerDetails, getMultipleElementDetails } from './handlers.js'


// Extract named cookie and return its value if exists
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


const sendPostRequest = async (endpoint, data, isJson = false) => {
    console.log('In sendPostRequest()');
    const headers = {
        'X-CSRFToken': getCookie('csrftoken')
    };
    if (isJson) {
        headers['Content-Type'] = 'application/json';
        data = JSON.stringify(data);
    }
    const response = await fetch(endpoint, {
        method: 'POST',
        credentials: 'include',
        headers: headers,
        body: data
    })
    console.log("Response status in sendrequest: ", response.status)
    return response
}


const sendGetRequest = async (endpoint, data, callback) => {
    const response = await fetch(endpoint, {
        method: 'GET'
    })
    return response
}

// const handleResponseForContentUpdate = async (response, newTitle, newDescripton) => {

// }

// const handleResponseForElementUpdate = async (response, elementName) => {
    
// }


function updateEventListeners() {

    const singleElementListenersList = getSingleHandlerDetails();
    const multipletElementListenersList = getMultipleElementDetails();


    singleElementListenersList.forEach(entry => {
        if (entry.element) {
            entry.element.removeEventListener(entry.event_name, entry.handler);
            entry.element.addEventListener(entry.event_name, entry.handler);
        }
    })
    for (let entry in singleElementListenersList) {
        if (entry.element) {
            entry.element.removeEventListener(entry.event_name, entry.handler);
            entry.elemnet.addEventListener(entry.event_name, entry.handler);
        }
    }

    multipletElementListenersList.forEach(entry => {
        if (entry.element) {
            entry.element.forEach(button => {
                button.removeEventListener(entry.event_name, entry.handler);
                button.addEventListener(entry.event_name, entry.handler);
            })
        }
    })
}


function updateContent(html, title, description) {
    document.getElementById("content").innerHTML = html;
	document.title = title;
	document.querySelector('meta[name="description"]').setAttribute("content", description);
    updateEventListeners();
}


function updateElementContent(html, elementId) {
    document.getElementById(elementId).innerHTML = html;
    updateEventListeners();
}


export { updateContent, updateElementContent, updateEventListeners, sendPostRequest, sendGetRequest }

