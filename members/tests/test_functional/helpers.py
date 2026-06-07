from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from members.models.person import Person


def complete_admin_signup(test, browser, department):
    """Fill out and submit the admin (captain) signup form.

    After an admin logs in, the consent middleware redirects users that do
    not have an ordinary user (Person) yet to the admin signup form, where
    one must be created before the rest of the site (incl. admin) can be
    reached. This helper fills out that form and waits for the resulting
    redirect to the family detail page.

    ``department`` must be an open department so it appears in the form's
    department dropdown.
    """
    try:
        WebDriverWait(browser, 10).until(EC.url_contains("admin_signup"))
    except Exception:
        test.fail("Was not redirected to the admin signup form")

    # Fill out the captain's (admin) signup form
    Select(browser.find_element(By.ID, "id_volunteer_gender")).select_by_value(
        Person.MALE
    )
    browser.find_element(By.ID, "id_volunteer_name").send_keys("Kaptajn Testperson")
    browser.find_element(By.ID, "id_volunteer_email").send_keys("captain@example.com")
    browser.find_element(By.ID, "id_volunteer_phone").send_keys("12345678")

    # The birthday is an <input type="date">, which expects an ISO value
    birthday = browser.find_element(By.ID, "id_volunteer_birthday")
    browser.execute_script("arguments[0].value = '1980-03-05';", birthday)

    Select(browser.find_element(By.ID, "id_volunteer_department")).select_by_value(
        str(department.pk)
    )

    # Enable manual address entry so the autofilled fields become editable
    browser.find_element(By.ID, "manual-entry").click()
    browser.find_element(By.ID, "id_streetname").send_keys("Testvej")
    browser.find_element(By.ID, "id_housenumber").send_keys("10")
    browser.find_element(By.ID, "id_zipcode").send_keys("5000")
    browser.find_element(By.ID, "id_city").send_keys("Odense C")

    # Submit the signup form
    browser.find_element(By.NAME, "submit").click()

    # Creating the person redirects to the family detail page
    try:
        WebDriverWait(browser, 10).until(EC.url_contains("family"))
    except Exception:
        test.fail("Admin signup form was not submitted successfully")
