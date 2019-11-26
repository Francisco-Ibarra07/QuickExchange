console.log("Background script running");

chrome.browserAction.onClicked.addListener(extensionButtonClicked);
chrome.browserAction.setBadgeText({text: "hi"}); // We have 10+ unread items.

// Callback function for browser action listener
// @arg tab is an object with a whole bunch of info about the tab
function extensionButtonClicked (tab) {
  let msg = {
    txt: "hello"
  }

  // Send messages to content scripts
  chrome.tabs.sendMessage(tab.id, txt);
}