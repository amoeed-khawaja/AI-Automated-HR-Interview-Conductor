﻿# AI-Automated-HR-Interview-Conductor

 # Interview Dashboard Automation

This project is an automated interview dashboard that scrapes LinkedIn profiles, formats candidate data into a dynamic interview prompt, and automates the process of injecting this prompt into a web-based assistant using browser automation. It features a React frontend for user input and a Flask backend for data processing and automation.

---

## Project Structure

```
backend/
    app.py                  # Flask backend server
    automate_chrome.py      # Chrome automation with Selenium
    linkedin_scraper.py     # LinkedIn profile scraper (pychrome)
    formatted_prompt.txt    # Temporary file for formatted prompt
    scrape.log              # Log file for scraping and automation
    static/
        internova.png
        internovabg.png

interview-dashboard/
    package.json            # Root React project config
    vite.config.js
    eslint.config.js
    index.html
    frontend/
        package.json        # Frontend React app config
        vite.config.js
        src/
            App.jsx        # Main React component
            App.css
            ...
        public/
            vite.svg
    public/
        vite.svg

static/
    index.css
    index.js
    css/
    js/
```

---

## Features

- **LinkedIn Scraping:** Extracts candidate name, bio, and experiences using a headless Chrome browser.
- **Dynamic Prompt Generation:** Formats scraped data into a customizable interview prompt template.
- **Browser Automation:** Uses Selenium to inject the prompt into a web dashboard (e.g., Vapi.ai).
- **React Frontend:** User-friendly form for submitting LinkedIn URLs and job titles.
- **Speech Recognition:** Frontend supports voice input for interviews (Web Speech API).
- **Logging:** All scraping and automation steps are logged for debugging.

---

## Setup Instructions

### 1. Backend (Flask)

#### Prerequisites

- Python 3.8+
- Chrome browser (with remote debugging enabled)
- [pip](https://pip.pypa.io/en/stable/)

#### Install Dependencies

```sh
cd backend
pip install flask selenium pychrome
```

#### Start Chrome with Remote Debugging

```sh
chrome --remote-debugging-port=9222
```

#### Run the Flask Server

```sh
python app.py
```

The server will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

### 2. Frontend (React)

#### Prerequisites

- Node.js 18+
- npm

#### Install Dependencies

```sh
cd interview-dashboard/frontend
npm install
```

#### Start the Development Server

```sh
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173) (or as specified by Vite).

---

## Usage

1. Open the frontend in your browser.
2. Enter a LinkedIn profile URL and the job title.
3. Submit the form.
4. The backend will scrape the LinkedIn profile, generate a formatted prompt, and automate pasting it into the assistant dashboard.
5. The frontend will enable voice input for the interview.

---

## Notes

- **LinkedIn scraping** requires that Chrome is running with remote debugging enabled.
- **Automation** targets a specific dashboard URL (configured in `automate_chrome.py`).
- **Speech recognition** works best in Chrome or Edge browsers.
- **Logs** are saved in `backend/scrape.log`.

---

## Customization

- Edit `backend/formatted_prompt.txt` or `paste.txt` to change the prompt template.
- Update selectors in `automate_chrome.py` if the target dashboard changes.
- Modify React components in `frontend/src/` for UI changes.

---

## License

This project is for educational and internal use only.

---

## Authors

- [Your Name]
