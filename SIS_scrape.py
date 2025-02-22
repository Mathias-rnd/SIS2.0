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

# Click the Component dropdown

dropdown = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "s2id_tfp-comp-js"))
)
dropdown.click()

# Wait explicitly for the options container to appear (adjust the class if necessary)
WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "select2-result-selectable"))
)

comps_list = driver.find_elements(By.CLASS_NAME, "select2-result-selectable")
for option in comps_list:
    if "Lecture" in option.text:
        option.click()
        break
else:
    print("'Lecture' option was not found!")


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



print("clicking on details")
details_links = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "status"))
)

for details in details_links:
    driver.execute_script("arguments[0].scrollIntoView();", details)
    driver.execute_script("arguments[0].click();", details)  # Click using JS
    time.sleep(2)  # Give some time to load details


### OVERALL LOOP ###
for i, element in enumerate(list_elements):
    try:
        course_name = element.text.strip()

        # Skip empty courses
        if not course_name or course_name in printed_courses:
            continue
        printed_courses.add(course_name)
        print(f"COURSE: {course_name}")

        # Get the overall section box of the course 
        class_container = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'tfp_accordion_row')]")
        # Get the different sections
        section_containers = class_container.find_elements(By.CLASS_NAME, "accorion-head")

        # Print professor names for each section
        for j, section in enumerate(section_containers):
            try:
                
                # Get section name
                section_name = "need to figure out"
                
                # Get professor/s
                faculty_elements = section.find_elements(By.CLASS_NAME, "tfp-ins")

                #Get Credits

                #Get Description

                #Get 

                # Extract unique faculty names
                faculty_list = list(set([faculty.get_attribute("textContent").strip() for faculty in faculty_elements if faculty.get_attribute("textContent").strip()]))

                # Print section and faculty information
                if faculty_list:
                    print(f" --> Section: {section_name}: {', '.join(faculty_list)}")

            except Exception as e:
                print(f"Error processing section {j+1}: {e}")

    except Exception as e:
        print(f"Error processing course {i+1}: {e}")



input("Press Enter to quit...")
driver.quit()
