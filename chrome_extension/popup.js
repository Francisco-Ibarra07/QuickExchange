console.log("Popup.js running");

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById("copyButton").addEventListener("click", copyButtonClickHandler);
  document.getElementById("popButton").addEventListener("click", popButtonClickHandler);
  document.getElementById("pushButton").addEventListener("click", pushButtonClickHandler);
  populateTextAreaElement();
});

// Fetch latest post url from Flask route
async function populateTextAreaElement() {
  try {
    const TEST_EMAIL = 'hmd@m.com';
    const response = await fetch('http://127.0.0.1:8080/get-latest-post?email=' + TEST_EMAIL);
    const data = await response.json();

    // console.log("Data recieved:");
    // console.log(JSON.stringify(data));

    // Set textarea value to fetched url
    if (data.hasOwnProperty('url')) {
      // console.log('url property: ', data['url']);
      let textareaElement = document.getElementById("currentStoredMediaBox");
      textareaElement.value = data['url'];
    } else {
      console.log('url property not found in: ', data);
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
    const TEST_EMAIL = "hmd@m.com";
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


