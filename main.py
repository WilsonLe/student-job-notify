import os
from pprint import pprint
from dotenv import load_dotenv
from time import sleep

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from contextlib import contextmanager
load_dotenv()
requestDelay = 10 # seconds
duoDelay = 60 # seconds
options = Options()
if os.getenv("PYTHON_ENV") == "production":
	options.add_argument('--headless')
driver = webdriver.Chrome(options=options)


try:
	# Go to root url
	driver.get(os.getenv("ROOT_URL"))
	wait(driver, requestDelay).until(EC.presence_of_element_located((By.ID, 'username')))

	# aEnter ID, PW
	driver.find_element_by_id("username").send_keys(os.getenv("ID"))
	driver.find_element_by_id("password").send_keys(os.getenv("PW"))
	driver.find_element_by_xpath('//*[@id="loginForm"]/div[6]/div/button').click()

	# Click Duo iframe
	wait(driver, requestDelay).until(EC.frame_to_be_available_and_switch_to_it("duo_iframe"))
	sleep(1)
	wait(driver, requestDelay).until(EC.presence_of_element_located((By.ID, "remember_me_label_text")))
	driver.find_element_by_id("remember_me_label_text").click()
	driver.find_element_by_xpath('//*[@id="auth_methods"]/fieldset/div[1]/button').click()
	driver.switch_to.default_content();

	# Wait until My Denison loads
	wait(driver, duoDelay).until(EC.presence_of_element_located((By.ID, 'mydenison-header')))
	print("Logged in")

	# Go to jobs
	driver.get('https://webapps.denison.edu/stuemp/search.php')
	lightRow = driver.find_elements_by_class_name("light-row")
	darkRow = driver.find_elements_by_class_name("dark-row")
	allRows = lightRow + darkRow
	allRows = list(map(lambda row: row.find_elements_by_tag_name('td'), allRows))

	# Extracting job general info
	jobs = []


	for row in allRows:
		href = row[0].find_element_by_tag_name('a').get_attribute('href')
		title = row[0].find_element_by_tag_name('a').text
		department = row[1].text
		jobs.append({
			"title": title,
			"href": href,
			"department": department
		})
	pprint(jobs)

except TimeoutException:
	print ("Loading took too much time!")
	driver.close()


