document.getElementById("form").addEventListener("submit", function (e) {
  e.preventDefault();

  // Show mic icon and animate it
  const micIcon = document.getElementById("mic-icon");
  micIcon.style.display = "block";

  // Optional: real voice input using Web Speech API (works over HTTPS)
  // const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  // recognition.start();
});
