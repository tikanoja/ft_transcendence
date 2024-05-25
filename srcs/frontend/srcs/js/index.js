import { getSingleHandlerDetails, getMultipleElementDetails } from './handlers.js'
import { routeRedirect } from './router.js'


// Extract named cookie and return its value if exists
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


const sendPostRequest = async (endpoint, data, isJson = false) => {
    
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
    });
    return response;
}


const sendGetRequest = async (endpoint) => {
    const response = await fetch(endpoint, {
        method: 'GET'
    });
    return response;
}

const handleResponseForContentUpdate = async (response, newTitle, newDescripton) => {
    
    if (response.redirected) {
        let redirect_location = response.url;
        routeRedirect(redirect_location);
    } else if (response.ok) {
        // handling normal content update
        const html = await response.text();
        updateContent(html, newTitle, newDescripton);
    } else {
        console.log('handleResponseForContentUpdate: response status: ' + response.status); //should this be an error log?
    }
}

const handleResponseForElementUpdate = async (response, elementName) => {
    
    if (response.redirected) {
		let redirect_location = response.url;
		routeRedirect(redirect_location);
	} else if (response.ok) {
		const html = await response.text();
		updateElementContent(html, elementName);
	} else {
		console.log("Response status in handleResponseForElementUpdate(): ", response.status)//should this be an error log?
	}
}


function updateEventListeners() {

    const singleElementListenersList = getSingleHandlerDetails();
    const multipletElementListenersList = getMultipleElementDetails();


    singleElementListenersList.forEach(entry => {
        if (entry.element) {
            entry.element.removeEventListener(entry.event_name, entry.handler);
            entry.element.addEventListener(entry.event_name, entry.handler);
        }
    })

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


export { updateContent, updateElementContent, updateEventListeners, sendPostRequest, sendGetRequest, handleResponseForContentUpdate, handleResponseForElementUpdate }
