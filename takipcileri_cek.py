from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

class InstagramFollowerScraper:
    def __init__(self, username, password, target_profile, headless=True):
        self.username = username
        self.password = password
        self.target_profile = target_profile

        # Headless mod için seçenekler
        options = Options()
        options.add_argument("--headless")  # Tarayıcıyı gizli modda çalıştırır
        options.add_argument("--disable-gpu")  # GPU'yu devre dışı bırakır
        options.add_argument("--no-sandbox")  # Sandbox'u devre dışı bırakır (Linux için)
        options.add_argument("--disable-dev-shm-usage")  # Bu seçenek, Docker gibi sanal ortamlarda faydalı olabilir

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

    def go_to_profile(self):
        self.browser.get(f"https://www.instagram.com/{self.target_profile}/")
        time.sleep(3)

    def open_followers_list(self):
        follow_buttons = self.browser.find_elements(By.CSS_SELECTOR, ".xl565be.x1m39q7l.x1uw6ca5.x2pgyrj")
        if len(follow_buttons) > 1:
            follow_button = follow_buttons[1]
            follow_button.click()
            time.sleep(5)

    def scroll_followers(self):
        js_command = """
        var followers = document.querySelector(".xyi19xy.x1ccrb07.xtf3nb5.x1pc53ja.x1lliihq.x1iyjqo2.xs83m0k.xz65tgg.x1rife3k.x1n2onr6");
        if (followers) {
            followers.scrollTo(0, followers.scrollHeight);
            return followers.scrollHeight;
        } else {
            return 0;
        }
        """
        len_of_page = self.browser.execute_script(js_command)
        match = False
        while not match:
            last_count = len_of_page
            time.sleep(15)
            len_of_page = self.browser.execute_script(js_command)
            if last_count == len_of_page:
                match = True
        time.sleep(3)

    def extract_followers(self):
        elements = self.browser.find_elements(By.CSS_SELECTOR,
            "a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n"
            ".x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5"
            ".x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.notranslate._a6hd"
        )
        followers = []
        for idx, element in enumerate(elements):
            href = element.get_attribute("href")
            if href:
                username = href.split("/")[-2]
                if username and username not in followers:
                    followers.append(username)
            # Her 200 kullanıcıdan sonra 30 saniye bekle
            if (idx + 1) % 200 == 0:
                print(f"{idx + 1} kullanıcı çekildi, 30 saniye bekleniyor...")
                time.sleep(30)
        return followers

    def save_to_file(self, followers, filename="takipciler.txt"):
        with open(filename, "w", encoding="UTF-8") as f:
            for follower in followers:
                f.write(follower + "\n")
        print(f"{len(followers)} takipçi başarıyla kaydedildi.")

    def run(self):
        try:
            self.login()
            self.go_to_profile()
            self.open_followers_list()
            self.scroll_followers()
            followers = self.extract_followers()
            self.save_to_file(followers)
        except Exception as e:
            print("Bir hata oluştu:", e)
        finally:
            self.browser.quit()
