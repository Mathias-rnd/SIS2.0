import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set Chrome options
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Hide automation flag
options.add_experimental_option("useAutomationExtension", False)  # Prevent Selenium extension

# Initialize WebDriver with options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open Tufts SIS
driver.get("https://sis.it.tufts.edu/psp/paprd/EMPLOYEE/EMPL/h/?tab=TFP_CLASS_SEARCH#class_search")

# ✅ Wait until page fully loads
WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")


# ✅ Click the Select2 dropdown
dropdown = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "tfp_clssrch_term"))
)
dropdown.click()


# ✅ Print all available options for debugging
options_list = driver.find_elements(By.CLASS_NAME, "select2-result-selectable")
print("\n🔍 Found options in the dropdown:")
for option in options_list:
    print(f"👉 {option.text}")

# ✅ Click "Spring 2025" if it exists
for option in options_list:
    if "Spring 2025" in option.text:
        print("✅ Found 'Spring 2025' - Clicking now!")
        option.click()
        break
else:
    print("❌ 'Spring 2025' option was not found!")
    
enter = driver.find_element(By.CLASS_NAME, "make3d") # selecting by class name
enter.click() # selenium allows us to click!

# ✅ Wait for the course results to load **after clicking search**
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "accorion-head"))
)
# ✅ Scroll until all courses are loaded
previous_count = 0
max_attempts = 15  # To prevent infinite loops
attempts = 0

while attempts < max_attempts:
    # Extract current list of courses
    list_elements = driver.find_elements(By.CLASS_NAME, "accorion-head")
    current_count = len(list_elements)

    # ✅ If no new courses are loading, stop scrolling
    if current_count == previous_count:
        print(f"✅ All courses loaded: {current_count} courses found.")
        break

    previous_count = current_count  # Update course count
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Allow time for new courses to load
    attempts += 1
    print(f"🔄 Scrolling... Found {current_count} courses so far.")

# ✅ Print all courses with their associated professors
print("\n📌 Found Courses:")
printed_courses = set()  # Track printed course names to avoid duplicates

for i, element in enumerate(list_elements):
    try:
        course_name = element.text.strip()

        # ✅ Skip empty courses
        if not course_name or course_name in printed_courses:
            continue
        
        printed_courses.add(course_name)  # Track unique courses

        # ✅ Find only the faculty names inside THIS course's container
        parent_container = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'tfp_accordion_row')]")
        faculty_elements = parent_container.find_elements(By.CLASS_NAME, "tfp-ins")

        # ✅ Extract unique faculty names
        faculty_list = list(set([faculty.get_attribute("textContent").strip() for faculty in faculty_elements if faculty.get_attribute("textContent").strip()]))

        print(f"👉 Course {i+1}: {course_name}")
        print(f"   👨‍🏫 Professors: {', '.join(faculty_list) if faculty_list else 'N/A'}")

    except Exception as e:
        print(f"   ❌ Error processing course {i+1}: {e}")



input("Press Enter to quit...")  # Keep browser open for debugging
driver.quit()
