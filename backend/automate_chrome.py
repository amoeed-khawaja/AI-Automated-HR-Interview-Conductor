import argparse
import json
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def force_paste_text(driver, textarea, text):
    """Multiple aggressive methods to force paste text"""
    
    print(f"🎯 Attempting to paste {len(text)} characters...")
    
    # Method 1: Direct JavaScript value setting with comprehensive events
    try:
        print("🚀 Method 1: Direct JavaScript injection...")
        
        # Use JSON.stringify to properly escape the text
        escaped_text = json.dumps(text)
        
        script = f"""
        var textarea = arguments[0];
        var text = {escaped_text};
        
        // Focus the element
        textarea.focus();
        
        // Set the value
        textarea.value = text;
        
        // Create and dispatch all possible events
        var events = ['input', 'change', 'keyup', 'keydown', 'paste'];
        events.forEach(function(eventType) {{
            var event = new Event(eventType, {{ bubbles: true, cancelable: true }});
            textarea.dispatchEvent(event);
        }});
        
        // Also try InputEvent
        var inputEvent = new InputEvent('input', {{ 
            bubbles: true, 
            cancelable: true,
            data: text 
        }});
        textarea.dispatchEvent(inputEvent);
        
        // Force a blur and focus to trigger validation
        textarea.blur();
        setTimeout(function() {{ textarea.focus(); }}, 100);
        
        return textarea.value.length;
        """
        
        result_length = driver.execute_script(script, textarea)
        
        if result_length > len(text) * 0.9:
            print(f"✅ Method 1 SUCCESS: {result_length} characters set!")
            return True
            
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Clipboard with multiple attempts
    try:
        print("📋 Method 2: Enhanced clipboard method...")
        import pyperclip
        
        # Clear clipboard first
        pyperclip.copy("")
        time.sleep(0.1)
        
        # Copy our text
        pyperclip.copy(text)
        time.sleep(0.2)
        
        # Verify clipboard
        clipboard_content = pyperclip.paste()
        if len(clipboard_content) < len(text) * 0.9:
            print("⚠️ Clipboard copy incomplete, trying again...")
            pyperclip.copy(text)
            time.sleep(0.5)
        
        # Multiple paste attempts
        for attempt in range(3):
            print(f"📝 Paste attempt {attempt + 1}/3...")
            
            # Click and focus
            textarea.click()
            time.sleep(0.3)
            
            # Select all
            textarea.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            
            # Paste using Ctrl+V
            textarea.send_keys(Keys.CONTROL + "v")
            time.sleep(0.5)
            
            # Check if it worked
            current_value = textarea.get_attribute('value')
            if len(current_value) > len(text) * 0.9:
                print(f"✅ Method 2 SUCCESS on attempt {attempt + 1}: {len(current_value)} characters!")
                
                # Trigger events manually
                driver.execute_script("""
                    var textarea = arguments[0];
                    ['input', 'change', 'blur', 'focus'].forEach(function(eventType) {
                        var event = new Event(eventType, { bubbles: true });
                        textarea.dispatchEvent(event);
                    });
                """, textarea)
                
                return True
                
        print("❌ Method 2: All paste attempts failed")
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Selenium ActionChains
    try:
        print("⚡ Method 3: ActionChains approach...")
        
        actions = ActionChains(driver)
        
        # Click, select all, and send text
        actions.click(textarea).perform()
        time.sleep(0.2)
        
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        time.sleep(0.2)
        
        # Send text in smaller chunks
        chunk_size = 500
        text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        for i, chunk in enumerate(text_chunks):
            print(f"📦 Sending chunk {i+1}/{len(text_chunks)}...")
            actions.send_keys(chunk).perform()
            time.sleep(0.1)
        
        # Verify
        current_value = textarea.get_attribute('value')
        if len(current_value) > len(text) * 0.9:
            print(f"✅ Method 3 SUCCESS: {len(current_value)} characters!")
            return True
            
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    # Method 4: Brute force character by character (last resort)
    try:
        print("💪 Method 4: Brute force character input...")
        
        textarea.click()
        time.sleep(0.2)
        textarea.send_keys(Keys.CONTROL + "a")
        time.sleep(0.2)
        
        # Send first 1000 characters to test
        test_chunk = text[:1000]
        textarea.send_keys(test_chunk)
        time.sleep(0.5)
        
        current_value = textarea.get_attribute('value')
        if len(current_value) > 500:
            print(f"✅ Method 4 partial SUCCESS: {len(current_value)} characters!")
            print("⚠️ Note: Only partial text due to size limitations")
            return True
            
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
    
    return False

def automate_textarea_with_data(url, formatted_prompt):
    """Selenium automation for textarea interaction with formatted prompt data"""
    driver = None
    try:
        # Chrome options to connect to existing instance
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        # Connect to existing Chrome instance
        print("🔗 Connecting to Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Open new tab and navigate
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load completely
        print("⏳ Waiting for page to load...")
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Additional wait for dynamic content
        time.sleep(5)
        
        # Wait for textarea to be present
        print("🔍 Looking for textarea...")
        wait = WebDriverWait(driver, 20)
        
        # Multiple selectors to try
        selectors = [
            'textarea[data-testid="system-prompt-textarea"]',
            'textarea[placeholder*="system"]',
            'textarea[placeholder*="prompt"]',
            'textarea',
            '[data-testid="system-prompt-textarea"]',
            '#system-prompt',
            '.system-prompt'
        ]
        
        textarea = None
        for selector in selectors:
            try:
                print(f"🎯 Trying selector: {selector}")
                textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"✅ Found textarea with selector: {selector}")
                break
            except:
                continue
        
        if not textarea:
            print("❌ Could not find textarea with any selector!")
            # Debug: list all textareas
            all_textareas = driver.find_elements(By.TAG_NAME, "textarea")
            print(f"🔍 Found {len(all_textareas)} textarea elements:")
            for i, ta in enumerate(all_textareas):
                attrs = {}
                for attr in ['data-testid', 'placeholder', 'class', 'id', 'name']:
                    try:
                        value = ta.get_attribute(attr)
                        if value:
                            attrs[attr] = value
                    except:
                        pass
                print(f"  📝 Textarea {i+1}: {attrs}")
            
            # Try first textarea if available
            if all_textareas:
                textarea = all_textareas[0]
                print("🎯 Using first available textarea...")
            else:
                raise Exception("No textarea elements found on page!")
        
        print("✅ Textarea found! Starting paste operation...")
        
        # Scroll to textarea
        driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
        time.sleep(1)
        
        # Show the text we're trying to paste (first 200 chars)
        print(f"📝 Text to paste (first 200 chars): {formatted_prompt[:200]}...")
        print(f"📏 Total length: {len(formatted_prompt)} characters")
        
        # PERSISTENT PASTE - keeps trying until it sticks
        print("🔄 Starting persistent paste operation...")
        
        for attempt in range(10):  # Try 10 times
            print(f"🎯 Attempt {attempt + 1}/10 - Forcing paste...")
            
            success = force_paste_text(driver, textarea, formatted_prompt)
            
            if success:
                # Wait and check if content is still there
                print("⏳ Waiting 2 seconds to check persistence...")
                time.sleep(2)
                
                current_value = textarea.get_attribute('value')
                if len(current_value) > len(formatted_prompt) * 0.8:
                    print(f"🎉 SUCCESS! Content persisted: {len(current_value)} characters!")
                    break
                else:
                    print(f"⚠️ Content disappeared! Only {len(current_value)} chars remain. Retrying...")
            else:
                print("❌ Paste failed, retrying...")
            
            # Short delay before retry
            time.sleep(1)
        
        # NUCLEAR OPTION - Set value and prevent any changes
        print("💥 NUCLEAR OPTION - Locking the content in place...")
        
        escaped_text = json.dumps(formatted_prompt)
        nuclear_script = f"""
        var textarea = arguments[0];
        var text = {escaped_text};
        
        // Set the value
        textarea.value = text;
        
        // Override the value property to always return our text
        Object.defineProperty(textarea, 'value', {{
            get: function() {{ return text; }},
            set: function(newValue) {{ 
                console.log('Attempted to change value, blocking it');
                return text; 
            }},
            configurable: false
        }});
        
        // Fire events
        ['input', 'change', 'focus', 'blur'].forEach(function(eventType) {{
            var event = new Event(eventType, {{ bubbles: true }});
            textarea.dispatchEvent(event);
        }});
        
        // Add mutation observer to prevent external changes
        var observer = new MutationObserver(function(mutations) {{
            if (textarea.value !== text) {{
                textarea.value = text;
                console.log('Value was changed externally, restoring our text');
            }}
        }});
        
        observer.observe(textarea, {{ 
            attributes: true, 
            attributeFilter: ['value'] 
        }});
        
        console.log('Nuclear option activated - content locked');
        return textarea.value.length;
        """
        
        try:
            result_length = driver.execute_script(nuclear_script, textarea)
            print(f"💥 Nuclear option executed: {result_length} characters locked!")
            
            # Wait to see if it holds
            time.sleep(3)
            final_check = textarea.get_attribute('value')
            print(f"🔒 Final lock check: {len(final_check)} characters")
            
        except Exception as e:
            print(f"❌ Nuclear option failed: {e}")
        
        # LAST RESORT - Continuous monitoring and re-pasting
        print("🛡️ LAST RESORT - Starting content guardian...")
        
        guardian_script = f"""
        var textarea = arguments[0];
        var targetText = {escaped_text};
        
        // Function to restore content
        function restoreContent() {{
            if (textarea.value !== targetText) {{
                textarea.value = targetText;
                ['input', 'change'].forEach(function(eventType) {{
                    var event = new Event(eventType, {{ bubbles: true }});
                    textarea.dispatchEvent(event);
                }});
                console.log('Content guardian restored text');
            }}
        }}
        
        // Set initial content
        restoreContent();
        
        // Monitor every 500ms
        var guardianInterval = setInterval(restoreContent, 500);
        
        // Stop guardian after 30 seconds
        setTimeout(function() {{
            clearInterval(guardianInterval);
            console.log('Content guardian stopped');
        }}, 30000);
        
        console.log('Content guardian started - will protect for 30 seconds');
        return 'Guardian activated';
        """
        
        try:
            result = driver.execute_script(guardian_script, textarea)
            print(f"🛡️ Content guardian result: {result}")
            print("🛡️ Guardian will protect content for 30 seconds!")
            
        except Exception as e:
            print(f"❌ Guardian failed: {e}")
        
        print("✅ Operation completed!")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Don't close the browser - let user see the result
        print("🔍 Browser left open for inspection")

def main():
    """Main function to handle command line arguments and run automation"""
    parser = argparse.ArgumentParser(description='URGENT Chrome automation with LinkedIn data')
    parser.add_argument('--linkedin-data', type=str, help='LinkedIn profile data as JSON string')
    parser.add_argument('--job-title', type=str, help='Job title the candidate is applying for')
    parser.add_argument('--prompt-file', type=str, help='Path to file containing formatted prompt')
    
    args = parser.parse_args()
    
    # Default URL
    url = "https://dashboard.vapi.ai/v2/assistants/94e635ef-eb8f-40e0-b1b6-3958d91241da"
    
    print("🚀 URGENT Chrome automation starting...")
    print("📋 Make sure Chrome is running with: chrome --remote-debugging-port=9222")
    print()
    
    # Read the formatted prompt from file
    formatted_prompt = ""
    if args.prompt_file:
        try:
            with open(args.prompt_file, 'r', encoding='utf-8') as f:
                formatted_prompt = f.read()
            print(f"📖 Loaded prompt from {args.prompt_file}")
            print(f"📏 Length: {len(formatted_prompt)} characters")
        except Exception as e:
            print(f"❌ Error reading prompt file: {e}")
            sys.exit(1)
    
    # Parse LinkedIn data if provided
    if args.linkedin_data:
        try:
            linkedin_data = json.loads(args.linkedin_data)
            candidate_name = linkedin_data.get('name', 'Unknown')
            print(f"👤 Candidate: {candidate_name}")
        except:
            print("⚠️ Warning: Could not parse LinkedIn data")
    
    if args.job_title:
        print(f"💼 Job: {args.job_title}")
    
    print("=" * 60)
    
    # Run the automation
    automate_textarea_with_data(url, formatted_prompt)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🧪 EMERGENCY TEST MODE...")
        
        try:
            with open('formatted_prompt.txt', 'r', encoding='utf-8') as f:
                formatted_prompt = f.read()
            print(f"📖 Found formatted_prompt.txt ({len(formatted_prompt)} chars)")
            
            url = "https://dashboard.vapi.ai/v2/assistants/94e635ef-eb8f-40e0-b1b6-3958d91241da"
            automate_textarea_with_data(url, formatted_prompt)
        except FileNotFoundError:
            print("❌ No formatted_prompt.txt found!")
            sys.exit(1)
    else:
        main()