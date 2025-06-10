const handleSubmit = async (e) => {
  e.preventDefault();
  
  console.log("🔵 Form submitted!");
  console.log("LinkedIn URL:", linkedin);
  console.log("Resume Name:", resumeName);

  // Disable the submit button
  const submitButton = e.target.querySelector('button[type="submit"]');
  if (submitButton) submitButton.disabled = true;

  try {
    console.log("🔵 Sending request to server...");
    
    const response = await fetch('http://127.0.0.1:5000/submit', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        linkedin: linkedin, 
        resumeName: resumeName 
      }),
    });
    
    console.log("🔵 Response status:", response.status);
    
    const data = await response.json();
    console.log("🔵 Server response:", data);
    
    if (data.status === 'success') {
      console.log("✅ LinkedIn URL sent successfully!");
      // Continue with your speech recognition code
      resetTranscript();
      setShowMic(true);
      await SpeechRecognition.startListening({ continuous: true });
      await setupVolumeListener();
    }
    
  } catch (error) {
    console.error("❌ Error submitting form:", error);
  } finally {
    // Re-enable the button
    if (submitButton) submitButton.disabled = false;
  }
};