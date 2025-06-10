import pychrome
import time
import json

def scrape_linkedin_profile(linkedin_url):
    # Set up the connection to the Chrome browser (assuming it's running on port 9222)
    browser = pychrome.Browser(url="http://127.0.0.1:9222")
    tab = browser.new_tab()
    tab.start()

    tab.call_method("Page.enable")
    tab.call_method("Runtime.enable")

    tab.call_method("Page.navigate", url=linkedin_url)
    time.sleep(10)  # Wait for the page to load dynamic content

    # JavaScript to scrape the profile data
    script = """
    (() => {
        const nameEl = document.querySelector('h1.t-24.v-align-middle');
        const bioEl = document.querySelector('[class*="text-body-medium"][class*="break-words"]');
        const experiences = [];

        const name = nameEl ? nameEl.innerText.trim() : "Name not found";
        const bio = bioEl ? bioEl.innerText.trim() : "Bio not found";

        const expItems = document.querySelectorAll('.artdeco-list__item');

        expItems.forEach(item => {
            const company = item.querySelector('.hoverable-link-text span[aria-hidden="true"]')?.innerText.trim() || '';
            const designation = item.querySelector('.display-flex.flex-column span[aria-hidden="true"]')?.innerText.trim() || '';
            const duration = item.querySelector('.t-black--light span[aria-hidden="true"]')?.innerText.trim() || '';
            const detail = item.querySelector('.inline-show-more-text--is-collapsed span[aria-hidden="true"]')?.innerText.trim() || '';

            const irrelevantDurations = ['followers', 'members', 'Published'];
            if (company.includes("3rd+") || duration.includes("3rd+") || irrelevantDurations.some(keyword => duration.includes(keyword))) {
                return;
            }

            if (company && designation && duration) {
                experiences.push({
                    company,
                    designation,
                    duration,
                    detail
                });
            }
        });

        return JSON.stringify({ name, bio, experiences });
    })()
    """

    # Run the JavaScript to get the data
    result = tab.call_method("Runtime.evaluate", expression=script, returnByValue=True)
    data = json.loads(result['result']['value'])
    tab.stop()
    return data
