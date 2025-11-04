"""
download_weather.py

This script uses Playwright to download the "30 Year Normals (daily)" CSV
from Toronto Weather Stats website with a row limit of 70000.

Requirements:
    pip install playwright
    playwright install chromium
"""

import os
import time
from playwright.sync_api import sync_playwright

# Configuration
DEST_FOLDER = "../data"
DEST_FILE = os.path.join(DEST_FOLDER, "toronto_weather_normals_daily.csv")
URL = "https://toronto.weatherstats.ca/download.html"
ROW_LIMIT = "70000"

# Create destination folder if it doesn't exist
os.makedirs(DEST_FOLDER, exist_ok=True)


def download_weather_csv():
    """
    Downloads the 30 Year Normals (daily) weather data from Toronto Weather Stats.
    
    The function:
    1. Opens the download page in a headless browser
    2. Selects the "30 Year Normals (daily)" radio button
    3. Sets the row limit to 70000
    4. Clicks the Download button
    5. Saves the downloaded CSV file to the data folder
    """
    
    with sync_playwright() as p:
        print("Launching browser...")
        
        # Launch browser in headless mode (set to False for debugging)
        browser = p.chromium.launch(headless=True)
        
        # Create a new context with download permissions
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        
        try:
            print(f"Navigating to {URL}...")
            page.goto(URL, wait_until="domcontentloaded")
            
            # Wait for the form to be visible
            print("Waiting for form to load...")
            page.wait_for_selector("input[type='radio']", timeout=15000)
            
            # Additional wait for any JavaScript to finish loading
            time.sleep(2)
            
            print("Selecting '30 Year Normals (daily)' option...")
            
            # Try to find the correct radio button by label text
            # Look for the radio button associated with "30 Year Normals (daily)"
            try:
                # Method 1: Try clicking by label text
                page.click("text=30 Year Normals (daily)")
                print("  ✓ Selected via label text")
            except:
                try:
                    # Method 2: Try finding by value attribute
                    all_radios = page.locator("input[type='radio']").all()
                    print(f"  Found {len(all_radios)} radio buttons")
                    
                    # The third radio button should be "30 Year Normals (daily)"
                    # Based on the order in the screenshot: 
                    # 0: Climate Daily/Forecast/Sun
                    # 1: Climate Hourly
                    # 2: 30 Year Normals (daily) ← This one!
                    # 3: 30 Year Normals (monthly)
                    all_radios[2].check()
                    print("  ✓ Selected third radio button (index 2)")
                except Exception as e:
                    print(f"  ✗ Error selecting radio: {e}")
                    # Debug: print all radio buttons
                    print("\n  Debug: Listing all radio buttons...")
                    for i, radio in enumerate(all_radios):
                        value = radio.get_attribute("value")
                        name = radio.get_attribute("name")
                        print(f"    Radio {i}: name='{name}', value='{value}'")
                    raise
            
            # Small delay to ensure the selection is registered
            time.sleep(1)
            
            print(f"Setting row limit to {ROW_LIMIT}...")
            # Find the row limit input field
            row_limit_input = page.locator("input[type='number'], input[name='limit']").first
            row_limit_input.click()
            row_limit_input.fill("")
            row_limit_input.fill(ROW_LIMIT)
            
            # Verify the value was set
            current_value = row_limit_input.input_value()
            print(f"  Row limit set to: {current_value}")
            
            # Small delay to ensure the value is set
            time.sleep(1)
            
            print("Clicking Download button...")
            # Set up download listener before clicking
            with page.expect_download(timeout=60000) as download_info:
                # Click the Download button - try multiple selectors
                try:
                    # Method 1: Try by exact text
                    download_button = page.get_by_role("button", name="Download")
                    download_button.click()
                    print("  ✓ Clicked via role button")
                except:
                    try:
                        # Method 2: Try by button element with text
                        page.click("button:text('Download')")
                        print("  ✓ Clicked via button text selector")
                    except:
                        # Method 3: Try any clickable element with "Download" text
                        page.click("text=Download")
                        print("  ✓ Clicked via text selector")
                
                print("Waiting for download to complete...")
                download = download_info.value
            
            # Save the downloaded file to the specified location
            print(f"Saving file to {DEST_FILE}...")
            download.save_as(DEST_FILE)
            
            # Get file size for confirmation
            file_size = os.path.getsize(DEST_FILE)
            print(f"✓ Download completed successfully!")
            print(f"  File: {DEST_FILE}")
            print(f"  Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
            
        except Exception as e:
            print(f"✗ Error occurred: {str(e)}")
            
            # Take a screenshot for debugging
            screenshot_path = "error_screenshot.png"
            page.screenshot(path=screenshot_path)
            print(f"  Screenshot saved to: {screenshot_path}")
            
            raise
            
        finally:
            # Clean up
            print("Closing browser...")
            time.sleep(2)  # Keep browser open briefly to see final state
            browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Toronto Weather Data Downloader")
    print("=" * 60)
    
    try:
        download_weather_csv()
        print("\n✓ Script completed successfully!")
    except Exception as e:
        print(f"\n✗ Script failed: {str(e)}")
        exit(1)