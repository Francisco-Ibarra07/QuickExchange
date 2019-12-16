console.log("Popup.js running");

// TODO(FI): Replace test email with actual email (USE WINDOWS global)
const TEST_EMAIL = "hmd@m.com";
const TEST_PASS = "asdf";
const DEV_URL = "http://127.0.0.1:5000";
document.addEventListener('DOMContentLoaded', function () {

  init()
    .then(() => {
      console.log("Starting init stuff");
      document.getElementById("loginButton").addEventListener("click", loginButtonClickHandler);
      document.getElementById("copyButton").addEventListener("click", copyButtonClickHandler);
      document.getElementById("popButton").addEventListener("click", popButtonClickHandler);
      document.getElementById("pushButton").addEventListener("click", pushButtonClickHandler);
      document.getElementById("showHistoryButton").addEventListener("click", showHistoryButtonClickHandler);
      populateTextAreaElement();
    })
    .catch((error) => {
      console.log(error);
      //document.getElementById("loginButton").addEventListener("click", loginButtonClickHandler);
    });
});

// Populates the 'window' global vars
function init() {
  return new Promise((resolve, reject) => {

    chrome.storage.sync.get(["jwt_token", "email"], function (result) {
      console.log("Result:", result);

      if (result.jwt_token === "" || result.email === "") {
        const errorMsg = {
          msg: "Empty results",
          error: [result.jwt_token, result.email]
        }
        console.log("Rejected");
        reject(errorMsg);
      }
      else {
        window.jwt_token = result.jwt_token;
        window.email = result.email
        console.log("Update successful");
        resolve();
      }
    });
  });
}

function showLoginModal() {
  document.querySelector("#login-modal").style.display = "flex";
}

function hideLoginModal() {
  document.querySelector("#login-modal").style.display = "none";
}

// TODO: Validate JWT token before allowing any requests to be made. If invalid redo login for user
function validateJWT() {

  if (window.jwt_token === "") {
    return false;
  }

  let parsedToken = parseJWT(window.jwt_token);
  console.log("pasredtoken: ", parsedToken);

  const now = Date.now();
  if (now >= parsedToken["exp"] * 1000) {
    console.log("now: ", now);
    console.log("token:", parsedToken.exp * 1000);
    return false;
  }

  console.log("TRUEEE");
  console.log("now: ", now);
  console.log("token:", parsedToken.exp);
  return true;
}

function parseJWT (token) {
  var base64Url = token.split('.')[1];
  var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  var jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
  }).join(''));

  return JSON.parse(jsonPayload);
}; 

function isValidEmail(email) {
  var regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return regex.test(String(email).toLowerCase());
}

function loginButtonClickHandler() {

  const email = document.getElementById("emailInput").value;
  const password = document.getElementById("passwordInput").value;

  if (email === "") {
    console.log("Email not provided");
    return;
  }
  else if (!isValidEmail(email)) {
    console.log("Email format is invalid");
    return;
  }
  else if (password === "") {
    console.log("Password not provided");
    return;
  }

  const targetURL = DEV_URL + "/auth";
  const fetchRequestData = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      "username": email,
      "password": password
    })
  }

  fetch(targetURL, fetchRequestData)
    .then((response) => {

      if (response.status === 401) {
        console.log("Password was incorrect!");
        return;
      }
      
      // Get token
      response.json().then((data) => {
        console.log(data);
        console.log("Everything checks out");
        console.log(email, password);

        // Store token in storage
        const storeMe = {
          "jwt_token": data["access_token"],
          "email": email
        }
        chrome.storage.sync.set(storeMe, function() {
          console.log("Data stored!");
          location.reload();
        })
      })
    })
    .catch((error) => {
      console.log("Fetch error: ", error);
    })
}

function showHistoryButtonClickHandler() {

  if(!validateJWT()) {
    console.log("JWT is currently invalid");
    showLoginModal();
    return;
  }
  else {
    hideLoginModal();
  }

  const targetURL = DEV_URL + "/get-history";
  const fetchRequestData = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'JWT ' + window.jwt_token
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


// Fetch latest post url from Flask route
function populateTextAreaElement() {

  if(!validateJWT()) {
    console.log("JWT is currently invalid");
    showLoginModal();
    return;
  }
  else {
    hideLoginModal();
  }

  const targetURL = DEV_URL + "/get-latest-post";
  const fetchRequestData = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'JWT ' + window.jwt_token
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

  if(!validateJWT()) {
    console.log("JWT is currently invalid");
    showLoginModal();
    return;
  }
  else {
    hideLoginModal();
  }

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
function pushButtonClickHandler(event) {

  if(!validateJWT()) {
    console.log("JWT is currently invalid");
    showLoginModal();
    return;
  }
  else {
    hideLoginModal();
  }

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
        'Content-Type': 'application/json',
        'Authorization': 'JWT ' + window.jwt_token
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
      headers: {
        'Authorization': 'JWT ' + window.jwt_token
      },
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
    // TODO: Show error messages when fetch fails. We can retry or show error message feedback/modal
    .catch((error) => {
      console.log(error);
    });
}