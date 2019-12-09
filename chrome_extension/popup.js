console.log("Popup.js running");

// TODO(FI): Replace test email with actual email
const TEST_EMAIL = "hmd@m.com";
const TEST_PASS = "asdf";
const DEV_URL = "http://127.0.0.1:5000";
document.addEventListener('DOMContentLoaded', function () {

  document.getElementById("copyButton").addEventListener("click", copyButtonClickHandler);
  document.getElementById("popButton").addEventListener("click", popButtonClickHandler);
  document.getElementById("pushButton").addEventListener("click", pushButtonClickHandler);
  document.getElementById("showHistoryButton").addEventListener("click", showHistoryButtonClickHandler);

  populateTextAreaElement();


  //test for modal
  // document.querySelector(".bg-modal").style.display = "none";
  //document.getElementById("loginButton").addEventListener("click", loginButtonClickHandler);
  //getToken();
});

function showHistoryButtonClickHandler() {
  const targetURL = DEV_URL + "/get-history";
  const fetchRequestData = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      "email": TEST_EMAIL
    })
  }

  fetch(targetURL, fetchRequestData)
    .then((response) => {
      if (response.status !== 200) {
        console.log("Error on show history. Status Code: " + response.status);
        return;
      }

      response.json().then((data) => {
        if (data.hasOwnProperty("history")) {
          for (let post of data["history"]) {
            console.log(post);
          }
        } else {
          console.log("No history key was returned");
        }
      })
    })
    .catch((error) => {
      console.log("Fetch error: ", error);
    })
}

async function loginButtonClickHandler() {}

async function storedTokenIsValid() {
  return false;
}

async function getToken() {

  try {
    const username = TEST_EMAIL;
    const password = TEST_PASS;
    const targetURL = DEV_URL + "/auth";
    const response = await fetch(targetURL, {
      headers: new Headers({
        'Authorization': 'Basic ' + btoa(username + ':' + password),
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
      await chrome.storage.sync.get(['token'], function (result) {
        console.log("Result:", result);
      });
    }


  } catch (error) {
    console.log(error);
  }
}


// Fetch latest post url from Flask route
function populateTextAreaElement() {

  const targetURL = DEV_URL + "/get-latest-post";
  const fetchRequestData = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      "email": TEST_EMAIL
    })
  }

  fetch(targetURL, fetchRequestData)
    .then((response) => {
      if (response.status !== 200) {
        console.log("Error on populate text area. Status Code: " + response.status);
        return;
      }

      response.json().then((data) => {
        let textareaElement = document.getElementById("currentStoredMediaBox");
        // Set textarea value to fetched url
        if (data.hasOwnProperty('url')) {
          textareaElement.value = data['url'];
        } else {
          console.log('url or message property not found in: ', data);
        }
      })
    })
    .catch((error) => {
      console.log("Fetch error: ", error);
    })
}

function copyButtonClickHandler(event) {
  let textareaElement = document.getElementById("currentStoredMediaBox");

  // Copy text to keyboard
  navigator.clipboard.writeText(textareaElement.value)
    .then(() => {
      console.log('Text copied to clipboard');
    })
    .catch((error) => {
      // This can happen if the user denies clipboard permissions:
      console.error('Could not copy text: ', error);
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
  const fileInput = document.getElementById("fileInput").files;

  if (urlInput === '' && fileInput.length === 0) {
    console.log("No url or file input found");
    return;
  } else if (urlInput !== '' && fileInput.length !== 0) {
    console.log("Can only have one or the other");
    return;
  }

  let fetchRequestData = '';
  let targetUrl = '';
  if (urlInput !== '') {

    if (!isValidUrl(urlInput)) {
      console.log("Invalid URL");
      return;
    }

    targetUrl = DEV_URL + '/create-url-post';
    fetchRequestData = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "url": urlInput,
        "email": TEST_EMAIL
      })
    }
  } else if (fileInput.length !== 0) {
    const formData = new FormData();
    formData.append('email', TEST_EMAIL);
    formData.append('file', fileInput[0]);

    targetUrl = DEV_URL + '/create-file-post';
    fetchRequestData = {
      method: 'POST',
      body: formData
    }
  }

  console.log("Testing fetchRequestData:", fetchRequestData);
  console.log("Sending to:", targetUrl);

  fetch(targetUrl, fetchRequestData)
    .then((response) => {

      if (response.status !== 201) {
        console.log("Error on creating file post. Status Code: " + response.status);
        return;
      }

      response.json().then((data) => {
        console.log("Response after fetch(): ", data);
        location.reload();
      })

    })
    .catch((error) => {
      console.log(error);
    });
}