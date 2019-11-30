console.log("Popup.js running");

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById("copyButton").addEventListener("click", copyButtonClickHandler);
  document.getElementById("popButton").addEventListener("click", popButtonClickHandler);
  document.getElementById("pushButton").addEventListener("click", pushButtonClickHandler);
  populateTextAreaElement();

  //test
  //getToken();
});

async function getToken() {

  try {
    const username = "hmd@m.com";
    const password = "asdf";
    const response = await fetch('http://127.0.0.1:8080/auth', { 
      headers: new Headers({
        'Authorization': 'Basic '+ btoa(username + ':' + password), 
        'Content-Type': 'application/x-www-form-urlencoded'
      })
    });

    const data = await response.json();
    console.log(data);

    // Store token if it was given
    if (data.hasOwnProperty('token')) {
      const token = data['token'];
      // How to store
      // await chrome.storage.sync.set({"token": token}, function() {
      //   console.log("Value stored!");
      // });

      // How to retrieve
      await chrome.storage.sync.get(['token'], function(result) {
        console.log("Result:",result);
      });
    }


  } catch (error) {
    console.log(error);
  }
}


// Fetch latest post url from Flask route
async function populateTextAreaElement() {
  try {
    const TEST_EMAIL = 'test@m.com';
    const response = await fetch('http://127.0.0.1:8080/get-latest-post?email=' + TEST_EMAIL);
    const data = await response.json();

    let textareaElement = document.getElementById("currentStoredMediaBox");
    // Set textarea value to fetched url
    if (data.hasOwnProperty('url')) {
      textareaElement.value = data['url'];
    } else {
      console.log('url or message property not found in: ', data);
    }
  } catch (error) {
    console.log(error);
  }
}

function copyButtonClickHandler(event) {
  let textareaElement = document.getElementById("currentStoredMediaBox");

  // Copy text to keyboard
  navigator.clipboard.writeText(textareaElement.value)
    .then(() => {
      console.log('Text copied to clipboard');
    })
    .catch(err => {
      // This can happen if the user denies clipboard permissions:
      console.error('Could not copy text: ', err);
    });
}

function popButtonClickHandler(event) {
  console.log("Pop button pressed");
  let textareaElement = document.getElementById("currentStoredMediaBox");
  const url = textareaElement.value;

  if (url === '') {
    console.log("Text area empty ; nothing to redirect to.")
    return;
  }

  var win = window.open(url, '_blank');
  win.focus();
}

// Quick function to test if a string is a url
const isValidUrl = (string) => {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;  
  }
}

// Will validate data and will call an async function to make the post request
async function pushButtonClickHandler(event) {
  const urlInput = document.getElementById("urlInput").value;
  if (urlInput === '') {
    console.log("No url input: ", urlInput);
    return;
  }

  // Validate URL
  if(!isValidUrl(urlInput)) {
    console.log("Invalid URL");
    return;
  }
  
  console.log("Sending url input: ", urlInput);
  try {
    // Create json data for post request
    // TODO(FI): Replace test email with actual email
    const TEST_EMAIL = "test@m.com";
    const dataToSend = {
      "url": urlInput,
      "email": TEST_EMAIL
    };

    // Create post request
    const response = await fetch('http://127.0.0.1:8080/set-post', {
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dataToSend)
    });
    
    // Wait for data 
    const responseData = await response.json();
    console.log("Response after fetch(): ", responseData);
    location.reload();
  } catch (error) {
    console.log(error);
  }
}


