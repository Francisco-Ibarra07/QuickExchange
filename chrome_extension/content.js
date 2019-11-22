console.log("This runs once web page loaded");

// For messages recieved from background script
chrome.runtime.onMessage.addListener(recievedMsg);
function recievedMsg(msg, sender, sendResponse) {
  console.log(msg.txt);
}