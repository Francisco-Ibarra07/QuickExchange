console.log("Popup.js running");

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById("copyButton").addEventListener("click", copyButtonClickHandler);
});

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