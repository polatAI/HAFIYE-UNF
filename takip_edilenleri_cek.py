from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

class InstagramScraper:
    def __init__(self, username, password, target_profile):
        self.username = username
        self.password = password
        self.target_profile = target_profile
        self.browser = None
        self.followers_list = []

    def setup_browser(self):
        options = Options()
        options.add_argument("--headless=new")  # Yeni headless mod
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Chrome(options=options)


    def login(self):
        self.browser.get("https://www.instagram.com/")
        time.sleep(5)

        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        login_button = self.browser.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/div[3]/button')
        login_button.click()
        time.sleep(5)

    def navigate_to_profile(self):
        self.browser.get(f"https://www.instagram.com/{self.target_profile}/")
        time.sleep(3)

        follow_buttons = self.browser.find_elements(By.CSS_SELECTOR, ".xl565be.x1m39q7l.x1uw6ca5.x2pgyrj")
        if len(follow_buttons) > 2:
            follow_button = follow_buttons[2]
            follow_button.click()
            time.sleep(5)

    def scroll_and_collect(self):
        js_command = """
        var takip_ettikleri = document.querySelector(".xyi19xy.x1ccrb07.xtf3nb5.x1pc53ja.x1lliihq.x1iyjqo2.xs83m0k.xz65tgg.x1rife3k.x1n2onr6");
        if (takip_ettikleri) {
            takip_ettikleri.scrollTo(0, takip_ettikleri.scrollHeight);
            return takip_ettikleri.scrollHeight;
        } else {
            return 0;
        }
        """
        len_of_page = self.browser.execute_script(js_command)
        match = False
        scroll_count = 0

        while not match:
            last_count = len_of_page
            time.sleep(15)
            len_of_page = self.browser.execute_script(js_command)
            if last_count == len_of_page:
                match = True

            followers_elements = self.browser.find_elements(
                By.CSS_SELECTOR,
                "a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n"
                ".x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5"
                ".x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.notranslate._a6hd"
            )

            for element in followers_elements:
                href = element.get_attribute("href")
                if href:
                    username = href.split("/")[-2]
                    if username and username not in self.followers_list:
                        self.followers_list.append(username)

            scroll_count += 1
            if scroll_count % 200 == 0:
                print(f"200 takipçi çekildi, 30 saniye bekleniyor...")
                time.sleep(30)

    def save_to_file(self, filename="takip_edilenler.txt"):
        with open(filename, "w", encoding="UTF-8") as f:
            for follower in self.followers_list:
                f.write(follower + "\n")
        print(f"{len(self.followers_list)} takipçi başarıyla kaydedildi.")

    def close_browser(self):
        if self.browser:
            self.browser.quit()

    def run(self):
        try:
            self.setup_browser()
            self.login()
            self.navigate_to_profile()
            self.scroll_and_collect()
            self.save_to_file()
        except Exception as e:
            print("Bir hata oluştu:", e)
        finally:
            self.close_browser()

