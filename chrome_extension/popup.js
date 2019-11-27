console.log("Popup.js running");

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById("copyButton").addEventListener("click", copyButtonClickHandler);
  document.getElementById("popButton").addEventListener("click", popButtonClickHandler);
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