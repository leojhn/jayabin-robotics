import time, traceback
from playwright.sync_api import sync_playwright

def test_flows():
    print("Beginning Playwright script...")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
        page = browser.new_page()

        print("Setting patient session in browser...")
        page.goto("http://localhost:8000/pages/checkin.html")
        page.evaluate('''() => {
            sessionStorage.setItem("patient", JSON.stringify({
                "PATIENT ID": "PAT-001",
                "PATIENT NAME": "John Doe",
                "AGE": 30,
                "GENDER": "Male"
            }));
        }''')

        print("Testing Welcome Skip Button...")
        page.goto("http://localhost:8000/pages/neo_nano_welcome.html")
        page.wait_for_selector("#skipBtn")
        page.click("#skipBtn")
        page.wait_for_url("**/appointments.html")
        print("Skip redirected to appointments.html successfully!")

        print("Testing Full Neo Nano Flow...")
        page.goto("http://localhost:8000/pages/neo_nano_welcome.html")
        page.click("#continueBtn")
        page.wait_for_url("**/neo_nano_symptoms.html")
        print("At neo_nano_symptoms.html")

        page.click("text=Fever")
        page.click("text=Headache")

        page.click("#nextBtn")
        page.wait_for_url("**/neo_nano_result.html")
        print("At neo_nano_result.html")

        page.wait_for_selector("#department", state="visible")
        time.sleep(2)

        dept_text = page.inner_text("#department")
        print("Analyzed Department:", dept_text)

        page.screenshot(path="/home/jules/verification/01_neo_nano_result.png")

        page.click("button:has-text('Continue')")
        page.wait_for_url("**/neo_nano_tests.html")
        print("At neo_nano_tests.html")

        page.screenshot(path="/home/jules/verification/02_neo_nano_tests.png")

        page.click("button:has-text('Continue to Appointment')")
        page.wait_for_url("**/appointments.html")
        print("At appointments.html")

        page.wait_for_selector("#department")
        time.sleep(1)

        selected_dept = page.eval_on_selector("#department", "el => el.value")
        print("Auto-selected Department in Appointments:", selected_dept)

        page.screenshot(path="/home/jules/verification/03_appointments_recommended.png")

        browser.close()
        print("All test flows completed successfully!")

if __name__ == "__main__":
    test_flows()
