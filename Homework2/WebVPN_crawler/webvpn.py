from selenium.webdriver.remote.webdriver import WebDriver as wd
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wdw
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
import selenium
from bs4 import BeautifulSoup as BS
import json

class WebVPN:
    def __init__(self, opt: dict, headless=False):
        self.root_handle = None
        self.driver: wd = None
        self.userid = opt["username"]
        self.passwd = opt["password"]
        self.headless = headless

    def login_webvpn(self):
        """
        Log in to WebVPN with the account specified in `self.userid` and `self.passwd`

        :return:
        """
        d = self.driver
        if d is not None:
            d.close()
        d = selenium.webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        d.get("https://webvpn.tsinghua.edu.cn/login")
        username = d.find_elements(By.XPATH,
                                   '//div[@class="login-form-item"]//input'
                                   )[0]
        password = d.find_elements(By.XPATH,
                                   '//div[@class="login-form-item password-field" and not(@id="captcha-wrap")]//input'
                                   )[0]
        username.send_keys(str(self.userid))
        password.send_keys(self.passwd)
        d.find_element(By.ID, "login").click()
        self.root_handle = d.current_window_handle
        self.driver = d
        return d

    def access(self, url_input):
        """
        Jump to the target URL in WebVPN

        :param url_input: target URL
        :return:
        """
        d = self.driver
        url = By.ID, "quick-access-input"
        btn = By.ID, "go"
        wdw(d, 5).until(EC.visibility_of_element_located(url))
        actions = AC(d)
        actions.move_to_element(d.find_element(*url))
        actions.click()
        actions.\
            key_down(Keys.CONTROL).\
            send_keys("A").\
            key_up(Keys.CONTROL).\
            send_keys(Keys.DELETE).\
            perform()

        d.find_element(*url)
        d.find_element(*url).send_keys(url_input)
        d.find_element(*btn).click()

    def switch_another(self):
        """
        If there are only 2 windows handles, switch to the other one

        :return:
        """
        d = self.driver
        assert len(d.window_handles) == 2
        wdw(d, 5).until(EC.number_of_windows_to_be(2))
        for window_handle in d.window_handles:
            if window_handle != d.current_window_handle:
                d.switch_to.window(window_handle)
                return

    def to_root(self):
        """
        Switch to the home page of WebVPN

        :return:
        """
        self.driver.switch_to.window(self.root_handle)

    def close_all(self):
        """
        Close all window handles

        :return:
        """
        while True:
            try:
                l = len(self.driver.window_handles)
                if l == 0:
                    break
            except selenium.common.exceptions.InvalidSessionIdException:
                return
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.close()

    def login_info(self):
        """
        TODO: After successfully logged into WebVPN, login to info.tsinghua.edu.cn

        :return:
        """
        d = self.driver
        self.access('info.tsinghua.edu.cn/')
        self.switch_another()
        wdw(d, 5).until(EC.visibility_of_element_located((By.XPATH,"//a[contains(@class, 'en_nav_link')]")))
        # 等待网站相应
        username = d.find_element(By.ID, 'userName')
        password = d.find_element(By.NAME, 'password')
        username.send_keys(str(self.userid))
        password.send_keys(self.passwd)
        d.find_element(By.XPATH,'//input[@type="image"]').click()
        wdw(d, 5).until(EC.visibility_of_element_located((By.XPATH,"//span[contains(@class, 'ml10')]")))
        # 输入账号密码登录
        self.driver = d
        return d
        # Hint: - Use `access` method to jump to info.tsinghua.edu.cn
        #       - Use `switch_another` method to change the window handle
        #       - Wait until the elements are ready, then preform your actions
        #       - Before return, make sure that you have logged in successfully
        # raise NotImplementedError

    def get_grades(self):
        """
        TODO: Get and calculate the GPA for each semester.

        Example return / print:
            2020-秋: *.**
            2021-春: *.**
            2021-夏: *.**
            2021-秋: *.**
            2022-春: *.**

        :return:
        """
        d = self.driver
        d.close()
        self.to_root()
        self.access('zhjw.cic.tsinghua.edu.cn/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw')
        self.switch_another()
        soup = BS(d.find_element(By.ID, 'table1').get_attribute('innerHTML'), 'lxml') 
        # 获取成绩单表格
        for (idex,i) in enumerate(soup.tbody.tr.find_all('th')) :
            if(i.text == '学分'): score_col = idex
            if(i.text == '绩点'): gpa_col = idex
            if(i.text == '学年-学期'): term_col = idex
        # 获取学分、绩点、学期所在栏编号
        term_gpa = {}
        for i in soup.tbody.find_all('tr'):
            info = i.find_all('td')
            if(len(info) < 6): continue
            term = info[term_col].text.strip()
            # 去除前后括号
            if(term_gpa.__contains__(term) == False): term_gpa[term] = [0,0.0]
            score = int(info[score_col].text)
            gpa = info[gpa_col].text.strip()
            if(gpa == 'N/A'): continue
            # 不计绩点科目
            term_gpa[term][0] += score
            term_gpa[term][1] += float(gpa) *  score
            # 计算每一个科目对应的学分与加权绩点并放入对应学期的字典中
        answer = {}
        for key,gpa_list in term_gpa.items():
            if(gpa_list[0] == 0): answer[key] = 0
            else:
                answer[key] = gpa_list[1] / gpa_list[0]
            # 计算每一个学期的均gpa并作为返回值
        return answer
        # Hint: - You can directly switch into
        #         `zhjw.cic.tsinghua.edu.cn/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw`
        #         after logged in
        #       - You can use Beautiful Soup to parse the HTML content or use
        #         XPath directly to get the contents
        #       - You can use `element.get_attribute("innerHTML")` to get its
        #         HTML code

        # raise NotImplementedError

if __name__ == "__main__":
    with open("./settings.json", "r", encoding="utf8") as f:
        infor = json.load(f)  # Load settings
    w = WebVPN(infor)
    w.login_webvpn()
    w.login_info()
    print(w.get_grades())
    