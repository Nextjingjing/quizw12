import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    print("Starting Functional Test...")

    # Navigate to /polls/
    driver.get("http://127.0.0.1:8000/polls/")

    # Wait for polls to appear
    polls = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li a"))
    )

    assert len(polls) > 0, "No polls available!"

    # Extract the initial rate of the first poll using regex
    first_poll = polls[0]
    poll_text = first_poll.text  # Example: "HOT: 1+1=? Rate: 51"

    match = re.search(r'Rate:\s*(\d+)', poll_text)  # Find 'Rate: 51'
    if not match:
        print(f"Skipping poll with no rate: {poll_text}")
        initial_rate = None  # Mark as skipped
    else:
        initial_rate = int(match.group(1))

    # Click on the first poll to vote
    first_poll.click()

    # Wait for voting page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "form"))
    )

    # Select the first available choice
    choices = driver.find_elements(By.NAME, "choice")
    assert len(choices) > 0, "No choices available to vote!"

    choices[0].click()

    # Submit the vote
    vote_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    vote_button.click()

    # Wait for results page
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Ensure "Vote again?" button exists
    vote_again_link = driver.find_element(By.LINK_TEXT, "Vote again?")
    assert vote_again_link is not None, "Vote again link not found!"

    # Go back to polls list
    driver.get("http://127.0.0.1:8000/polls/")

    # Wait for polls to appear again
    polls_after_vote = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li a"))
    )

    # Extract updated rate using regex
    updated_poll_text = polls_after_vote[0].text
    match = re.search(r'Rate:\s*(\d+)', updated_poll_text)
    if not match:
        print(f"Skipping poll with no rate after vote: {updated_poll_text}")
        updated_rate = None  # Mark as skipped
    else:
        updated_rate = int(match.group(1))

    # Verify rate increased if the poll had a rate
    if initial_rate is not None and updated_rate is not None:
        assert updated_rate == initial_rate + 1, f"Rate did not increase correctly! Expected: {initial_rate + 1}, Got: {updated_rate}"

    # ---- CATEGORIZATION CHECK (WITHOUT "NORMAL" LABEL) ----
    all_tests_passed = True  # Track test status

    # Loop through all polls and check their category
    for poll in polls_after_vote:
        poll_text = poll.text  # Example: "HOT: 1+1=? Rate: 51"

        # Extract the rate using regex
        match = re.search(r'Rate:\s*(\d+)', poll_text)
        if not match:
            print(f"Skipping poll without rate: {poll_text}")
            continue  # Skip if no rate found

        rate = int(match.group(1))

        # Determine displayed category (HOT, WARM, or BLANK)
        if "HOT:" in poll_text:
            detected_category = "HOT"
        elif "WARM:" in poll_text:
            detected_category = "WARM"
        else:
            detected_category = ""  # Blank for rates ≤ 10

        # Expected category based on rate
        if rate > 50:
            expected_category = "HOT"
        elif rate > 10:
            expected_category = "WARM"
        else:
            expected_category = ""  # No label if rate ≤ 10

        # Validate category
        if detected_category != expected_category:
            print(f"Assertion Failed: Poll categorization incorrect! Expected: '{expected_category}', Got: '{detected_category}' (Rate: {rate})")
            all_tests_passed = False

    if all_tests_passed:
        print("Pass all tests")

except AssertionError as e:
    print(f"Assertion Failed: {e}")
except Exception as e:
    print(f"Test Failed: {e}")
finally:
    # Close WebDriver
    driver.quit()
