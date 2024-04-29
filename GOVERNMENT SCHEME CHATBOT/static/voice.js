const toggleBtn = document.getElementById('toggle-btn');
const outputTextarea = document.getElementById('user-input');
let recognition;

toggleBtn.addEventListener('click', () => {
    if (!recognition) {
        startRecognition();
    } else {
        stopRecognition();
    }
});

function startRecognition() {
  recognition = new webkitSpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = true;
  recognition.interimResults = false;

  recognition.onresult = function(event) {
      const result = event.results[event.results.length - 1];
      const transcript = result[0].transcript;
      outputTextarea.value = transcript;
      sendUserQuery(transcript); // Pass the recognized text to sendUserQuery() function
  };

  recognition.onend = function() {
      toggleBtn.innerHTML = '<i id="toggle-btn" style="font-size:24px; color:green;" class="fa">&#xf130;</i>';
      outputTextarea.placeholder = 'Your speech will appear here...';
  };

  recognition.start();

  toggleBtn.innerHTML = '<i id="toggle-btn" style="font-size:24px; color:red;" class="fa">&#xf130;</i>';
  outputTextarea.value = '';
  outputTextarea.placeholder = 'Listening...';

  // Automatically stop recognition after 5 seconds (adjust as needed)
  setTimeout(stopRecognition,5000);
}


function stopRecognition() {
    if (recognition) {
        recognition.stop();
        recognition = null;
    }
}
