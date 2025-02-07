import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# Initialize WebDriver with options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open Tufts SIS
driver.get("https://sis.it.tufts.edu/psp/paprd/EMPLOYEE/EMPL/h/?tab=TFP_CLASS_SEARCH#class_search")

#Wait until page fully loads
WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")


# Click the Class Term dropdown
dropdown = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "tfp_clssrch_term"))
)
dropdown.click()

# Select Spring 2025
options_list = driver.find_elements(By.CLASS_NAME, "select2-result-selectable")
for option in options_list:
    if "Summer 2025" in option.text:
        option.click()
        break
else:
    print("'Summer 2025' option was not found!")

# Click the Search button
enter = driver.find_element(By.CLASS_NAME, "make3d")
enter.click()

# Wait for the search results (first) to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "accorion-head"))
)


previous_count = 0
max_attempts = 15  # To prevent infinite loops
attempts = 0

# While loop to scroll until all courses are loaded
while attempts < max_attempts:
    # Extract current list of courses
    list_elements = driver.find_elements(By.CLASS_NAME, "accorion-head")
    current_count = len(list_elements)
    if current_count == previous_count:
        break

    previous_count = current_count
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Allow time for new courses to load
    attempts += 1

print("\nFound Courses:")
printed_courses = set()  # Track printed course names to avoid duplicates

# print("clicking on details")
# details_links = WebDriverWait(driver, 10).until(
#     EC.presence_of_all_elements_located((By.CLASS_NAME, "status"))
# )

# for details in details_links:
#     driver.execute_script("arguments[0].scrollIntoView();", details)
#     driver.execute_script("arguments[0].click();", details)  # Click using JS
#     time.sleep(2)  # Give some time to load details

for i, element in enumerate(list_elements):
    try:
        course_name = element.text.strip()

        #Skip empty courses
        if not course_name or course_name in printed_courses:
            continue
        
        printed_courses.add(course_name)  # Track unique courses
        print(f"COURSE:  {course_name}")
        

        # #Find only the faculty names inside THIS course's container
        class_container = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'tfp_accordion_row')]")
        section_container = class_container.find_elements(By.CSS_SELECTOR, ".accorion-head.closed")

        print("Found section containers:", len(section_container))
        # section_elements = parent_container.find_elements(By.XPATH, "//tr[contains(@class, 'accorion-head')]/td[1]")

        faculty_elements = section_container[1].find_element(By.CLASS_NAME, "tfp-ins")

        # Extract unique faculty names
        faculty_list = list(set([faculty.get_attribute("textContent").strip() for faculty in faculty_elements if faculty.get_attribute("textContent").strip()]))
        
        print(f"Professor(s): {', '.join(faculty_list) if faculty_list else 'N/A'}")

        details_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "status"))
        )
        # driver.execute_script("arguments[0].scrollIntoView();", details_links[i])
        # driver.execute_script("arguments[0].click();", details_links[i])  # Click using JS
        # time.sleep(2)  # Give some time to load details

    except Exception as e:
        print(f"Error processing course {i+1}: {e}")



input("Press Enter to quit...")  # Keep browser open for debugging
driver.quit()
