import subprocess
import json
import sys
from flask import Flask, request, jsonify, render_template_string
from linkedin_scraper import scrape_linkedin_profile
import logging

logging.basicConfig(
    filename='scrape.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

def format_linkedin_data_for_prompt(profile_data, job_title, base_prompt):
    """
    Function to format LinkedIn scraped data and inject it into the base prompt
    
    Args:
        profile_data (dict): LinkedIn profile data from scraper
        job_title (str): Job title the candidate is applying for
        base_prompt (str): Base interview prompt template
    
    Returns:
        str: Formatted prompt with LinkedIn data injected
    """
    try:
        # Extract individual parts from profile data
        name = profile_data.get("name", "Name not found")
        bio = profile_data.get("bio", "Bio not found")
        experiences = profile_data.get("experiences", [])
        education = profile_data.get("education", [])
        skills = profile_data.get("skills", [])
        
        # Format client data section
        client_data_section = f"""
CANDIDATE PROFILE:
==================
Name: {name}

Bio/Summary: {bio}

Work Experience:
"""
        
        # Add experiences
        if experiences:
            for idx, exp in enumerate(experiences, 1):
                designation = exp.get('designation', 'N/A')
                company = exp.get('company', 'N/A')
                duration = exp.get('duration', 'N/A')
                detail = exp.get('detail', 'No details available')
                
                client_data_section += f"""
{idx}. {designation} at {company}
   Duration: {duration}
   Details: {detail}
"""
        else:
            client_data_section += "\nNo work experience found.\n"
        
        # Add education if available
        if education:
            client_data_section += "\nEducation:\n"
            for idx, edu in enumerate(education, 1):
                degree = edu.get('degree', 'N/A')
                school = edu.get('school', 'N/A')
                duration = edu.get('duration', 'N/A')
                client_data_section += f"{idx}. {degree} - {school} ({duration})\n"
        
        # Add skills if available
        if skills:
            client_data_section += f"\nSkills: {', '.join(skills[:10])}"  # Limit to first 10 skills
            if len(skills) > 10:
                client_data_section += f" and {len(skills) - 10} more..."
        
        # Replace placeholders in the base prompt
        formatted_prompt = base_prompt.replace(
            "Client data=  \n`\n`", 
            f"Client data=  \n`{client_data_section}\n`"
        )
        
        formatted_prompt = formatted_prompt.replace(
            "Job Title= \n`\n`", 
            f"Job Title= \n`{job_title}\n`"
        )
        
        return formatted_prompt
        
    except Exception as e:
        print(f"Error formatting LinkedIn data: {e}")
        logging.error(f"Error formatting LinkedIn data: {e}")
        return base_prompt  # Return original prompt if formatting fails

# Your HTML template as a string (keeping the same as before)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: black;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 100%;
            max-width: 500px;
            text-align: center;
        }

        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5rem;
            font-weight: 700;
        }

        .form-group {
            margin-bottom: 25px;
            text-align: left;

        }

        label {
            display: block;
            margin-bottom: 8px;
            color: pink;
            font-weight: 600;
            font-size: 1.1rem;
        }

        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background: white;
        }

        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            margin-top: 10px;
        }

        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }

        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .mic-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
            display: none;
        }

        .mic-section.show {
            display: block;
        }

        .mic-button {
            background: #ff6b6b;
            color: white;
            border: none;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            font-size: 2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px;
        }

        .mic-button:hover {
            background: #ff5252;
            transform: scale(1.1);
        }

        .mic-button.listening {
            background: #4caf50;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .transcript {
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 10px;
            min-height: 100px;
            text-align: left;
            border: 2px solid #e1e1e1;
        }

        .status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 8px;
            font-weight: 600;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .volume-indicator {
            width: 100%;
            height: 10px;
            background: #e1e1e1;
            border-radius: 5px;
            margin: 10px 0;
            overflow: hidden;
        }

        .volume-bar {
            height: 100%;
            background: linear-gradient(90deg, #4caf50, #ff9800, #f44336);
            width: 0%;
            transition: width 0.1s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- <h1>🎤 Interview Dashboard</h1> -->
        <img src="{{ url_for('static', filename='internovabg.png') }}" alt="Internova Logo">

        <form id="interviewForm">
            <div class="form-group">
                <label for="linkedin">LinkedIn Profile URL:</label>
                <input 
                    type="text" 
                    id="linkedin" 
                    name="linkedin" 
                    placeholder="https://linkedin.com/in/your-profile"
                    required
                >
            </div>
            
            <div class="form-group">
                <label for="resumeName">Job Title:</label>
                <input 
                    type="text" 
                    id="resumeName" 
                    name="resumeName" 
                    placeholder="Job you are applying for"
                    required
                >
            </div>
            
            <button type="submit" class="submit-btn" id="submitBtn">
                Start Interview 🚀
            </button>
        </form>

        <div id="status"></div>

        <div class="mic-section" id="micSection">
            <h3>🎤 Voice Recording Active</h3>
            <button class="mic-button" id="micButton" title="Click to toggle recording">
                🎤
            </button>
            <div class="volume-indicator">
                <div class="volume-bar" id="volumeBar"></div>
            </div>
            <div class="transcript" id="transcript">
                <em>Speak now... Your words will appear here.</em>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let recognition;
        let isListening = false;
        let transcript = '';

        // DOM elements
        const form = document.getElementById('interviewForm');
        const linkedinInput = document.getElementById('linkedin');
        const resumeNameInput = document.getElementById('resumeName');
        const submitBtn = document.getElementById('submitBtn');
        const statusDiv = document.getElementById('status');
        const micSection = document.getElementById('micSection');
        const micButton = document.getElementById('micButton');
        const transcriptDiv = document.getElementById('transcript');
        const volumeBar = document.getElementById('volumeBar');

        // Initialize Speech Recognition
        function initSpeechRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'en-US';

                recognition.onstart = () => {
                    console.log('🎤 Speech recognition started');
                    isListening = true;
                    micButton.classList.add('listening');
                    micButton.textContent = '🔴';
                };

                recognition.onresult = (event) => {
                    let interimTranscript = '';
                    let finalTranscript = '';

                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        const transcriptPart = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            finalTranscript += transcriptPart;
                        } else {
                            interimTranscript += transcriptPart;
                        }
                    }

                    transcript = finalTranscript;
                    transcriptDiv.innerHTML = `
                        <strong>Final:</strong> ${finalTranscript}<br>
                        <em>Interim:</em> ${interimTranscript}
                    `;
                };

                recognition.onerror = (event) => {
                    console.error('Speech recognition error:', event.error);
                    showStatus('Speech recognition error: ' + event.error, 'error');
                };

                recognition.onend = () => {
                    console.log('🎤 Speech recognition ended');
                    isListening = false;
                    micButton.classList.remove('listening');
                    micButton.textContent = '🎤';
                };

                return true;
            } else {
                console.error('Speech recognition not supported');
                showStatus('Speech recognition not supported in this browser', 'error');
                return false;
            }
        }

        // Setup volume monitoring (simulated)
        function setupVolumeListener() {
            setInterval(() => {
                if (isListening) {
                    // Simulate volume levels
                    const volume = Math.random() * 100;
                    volumeBar.style.width = volume + '%';
                }
            }, 100);
        }

        // Handle form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const linkedin = linkedinInput.value.trim();
            const resumeName = resumeNameInput.value.trim();

            console.log("🔵 Form submitted!");
            console.log("LinkedIn URL:", linkedin);
            console.log("Job Title:", resumeName);

            // Disable submit button
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            try {
                console.log("🔵 Sending request to server...");
                
                const response = await fetch('/submit', {
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
                    showStatus('✅ Data submitted successfully! Starting interview...', 'success');
                    
                    // Show mic section and start recording
                    micSection.classList.add('show');
                    
                    // Initialize speech recognition if not already done
                    if (!recognition && initSpeechRecognition()) {
                        setupVolumeListener();
                    }
                    
                    // Start listening
                    if (recognition && !isListening) {
                        recognition.start();
                    }
                } else {
                    showStatus('❌ Error: ' + data.message, 'error');
                }
                
            } catch (error) {
                console.error("❌ Error submitting form:", error);
                showStatus('❌ Connection error. Make sure the Flask server is running.', 'error');
            } finally {
                // Re-enable submit button
                submitBtn.disabled = false;
                submitBtn.textContent = 'Start Interview 🚀';
            }
        });

        // Handle mic button click
        micButton.addEventListener('click', () => {
            if (!recognition) {
                if (!initSpeechRecognition()) {
                    return;
                }
                setupVolumeListener();
            }

            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });

        // Show status messages
        function showStatus(message, type) {
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
            
            // Hide after 5 seconds
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            console.log('🚀 Interview Dashboard loaded');
            
            // Check if speech recognition is available
            if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
                showStatus('⚠️ Speech recognition not supported in this browser. Try Chrome or Edge.', 'error');
            }
        });
    </script>
</body>
</html>
'''

# Simple CORS handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit', methods=['POST', 'OPTIONS'])
def handle_submit():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        linkedin_url = data.get('linkedin', '')
        job_title = data.get('resumeName', '')

        print(f"📎 LINKEDIN URL: {linkedin_url}")
        logging.info(f"LINKEDIN URL: {linkedin_url}")

        print(f"📄 JOB TITLE: {job_title}")
        print("=" * 50)

        # Scrape LinkedIn profile data
        profile_data = scrape_linkedin_profile(linkedin_url)

        # Extract and print individual parts
        name = profile_data.get("name", "Name not found")
        bio = profile_data.get("bio", "Bio not found")
        experiences = profile_data.get("experiences", [])

        print(f"👤 NAME: {name}")
        logging.info(f"NAME: {name}")
        print(f"\n📝 BIO: {bio}")
        print("\n💼 EXPERIENCES:")
        if experiences:
            for idx, exp in enumerate(experiences, 1):
                print(f"  {idx}. {exp.get('designation', 'N/A')} at {exp.get('company', 'N/A')}")
                print(f"     Duration: {exp.get('duration', 'N/A')}")
                print(f"     Detail: {exp.get('detail', 'No details')}\n")
        else:
            print("  No experience data found.")

        print("=" * 50 + "\n")

        # Read the base interview prompt from paste.txt
        try:
            with open('paste.txt', 'r', encoding='utf-8') as f:
                base_prompt = f.read()
        except FileNotFoundError:
            print("❌ Warning: paste.txt not found. Using default prompt.")
            base_prompt = """
""Can you start by introducing yourself—your academic background and your most recent role or internship?"

"Also, what inspired you to apply for the [Job Title] position with us?"

🧠 Experience & Relevance to the [Job Title]

"Looking at your role at [Last Company Name from resume], how do you think that prepared you for a [Job Title] position?"

"You worked on [key task or responsibility from resume]. Could you explain how that might relate to what you'd be doing in this role?"

"You’ve listed skills like [skills from resume related to JD]. Could you share an example where you applied one of them to solve a real problem?"

🎓 Education & Applied Knowledge

"You studied [Degree Name] at [University Name]. How have you applied what you learned to any real-world projects or jobs?"

"I see you took courses like [Relevant Course 1] and [Course 2]—how did those help shape your understanding of the kind of work you'd do as a [Job Title]?"

🔍 Resume-Based Project Inquiry

"You worked on a project called [Project Name from resume]. That sounds interesting—what specific challenges did you face in that, and how did you tackle them?"

"I noticed your work on [second project or internship]—how is that experience relevant to the kind of goals we have for our [Job Title] role?"

(If multiple projects are present, rotate between them in a follow-up.)

🎯 Role-Specific Scenarios for [Job Title]

Ask 2–3 relevant questions from this list, adapting to the role:

If [Job Title] = Sales Manager or Business Development:

"Tell me about a time you exceeded your sales target. What did you do differently?"

"How do you typically build and retain long-term client relationships?"

If [Job Title] = Software Engineer / Developer / Technical:

"You mentioned using tools like [Tool/Language from resume]—what’s your favorite stack and why?"

"Walk me through a technical challenge you faced recently and how you resolved it."

If [Job Title] = Teacher / Student Affairs / Academic:

"How do you engage students or participants in your sessions?"

"Have you ever managed a tough classroom or learning situation? What was your approach?"

If [Job Title] = Support / Admin / Customer-Facing:

"How do you typically calm down a frustrated client or customer?"

"Can you describe a time you had to respond quickly under pressure?"

If [Job Title] = Arts / Creative / Design:

"Your project/work on [Creative project from resume] is quite unique. What inspired that?"

"How do you balance creative freedom with client or brand guidelines?"

If [Job Title] = Banking / Finance:

"How do you ensure accuracy in reporting or transaction handling?"

"Tell me about a high-pressure financial decision or situation you've been involved in."

🤝 Soft Skills & Team Fit

"You’ve listed leadership roles like [leadership role from resume]—what did you learn from those experiences?"

"How do you usually deal with deadlines and multitasking?"

"Do you prefer solo work or team-based environments? Can you share a quick example?"

(Short positive reinforcement is okay: “That’s a good balance,” or “Sounds like you collaborate well.”)

🗓️ Availability & Practical Questions

"Are you currently working or available to join immediately?"

"What are your salary expectations for this position?"

"Are you open to relocation or working remotely if required?"

📌 Wrap-Up and Next Steps

"Thank you for sharing your insights."

"Based on the experience and the role of [Job Title], our company’s budget range is PKR 80k to 120k."

"We’ll now forward your profile to the hiring manager. If shortlisted, you’ll hear back from us within 2–3 business days."

🙏 Closing

"Thanks again for your time today. We appreciate your interest in joining our team. Have a great day!"

⚙️ System Instructions for the Interview Bot
Dynamically replace [Job Title] with provided input.

Extract resume fields like: name, education, last job title, projects, tools/technologies, leadership roles, and certifications.

Ask questions based on resume highlights and job relevance.

React only to spoken content—ignore any background noise or voices unless the candidate themselves is speaking.

If candidate doesn’t respond, do not interrupt. Wait or prompt gently:
“Let me know when you're ready to continue.”

"

Client data=  
`
`

Job Title= 
`
`
"""

        # Format the LinkedIn data into the prompt
        formatted_prompt = format_linkedin_data_for_prompt(profile_data, job_title, base_prompt)

        print("📝 FORMATTED PROMPT READY")
        print("🤖 Starting Chrome automation...")

        # Save the formatted prompt to a temporary file for the automation script
        with open('formatted_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(formatted_prompt)

        # Trigger the automation script with parameters
        # Pass the formatted prompt text as a command line argument
        subprocess.Popen([
            "python", 
            "automate_chrome.py", 
            "--linkedin-data", json.dumps(profile_data),
            "--job-title", job_title,
            "--prompt-file", "formatted_prompt.txt"
        ])

        return jsonify({
            "status": "success",
            "message": "Profile scraped successfully! Chrome automation started with LinkedIn data.",
            "profile": profile_data,
            "formatted_prompt_preview": formatted_prompt[:500] + "..." if len(formatted_prompt) > 500 else formatted_prompt
        })

    except Exception as e:
        print(f"❌ ERROR: {e}")
        logging.error(f"ERROR: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Flask server starting...")
    print("📍 Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True, port=5000, host='127.0.0.1')