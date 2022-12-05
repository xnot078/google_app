# %%
# web
from selenium import webdriver, common
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# basic
import time, random, re, datetime, os
import pandas as pd
# typing
from typing import Optional, List
from dataclasses import dataclass, asdict


def InitDriver(webdrive_path = './chromedriver.exe',
			   incognito = True, 
			   headless = True):
    chrome_options = Options()
    # chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    if incognito:
    	chrome_options.add_argument("incognito")
    if headless:
    	chrome_options.add_argument("--headless")
    Driver = webdriver.Chrome(webdrive_path, chrome_options = chrome_options)
    Driver.implicitly_wait(0.5)
    return Driver

@dataclass
class App_Info:
    name: Optional[str] = None
    owner: Optional[str] = None
    avg_rate: Optional[float] = None
    downloads: Optional[float] = None
    age_certify: Optional[str] = None
    last_update: Optional[str] = None
    rank_dist: List[float] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class Commit:
    author: Optional[str] = None
    rate: Optional[float] = None
    date: Optional[str] = None
    text: Optional[str] = None
    likes: Optional[float] = None

    def to_dict(self):
        return asdict(self)

    
class app_detail:
    
    def __init__(self,
                 url: str,
                 driver: Optional[webdriver.chrome.webdriver.WebDriver] = None): 
        if driver is None:
            driver = InitDriver()
        self.driver = driver
        self.driver.get(url)
        self.app_info: Optional[App_Info] = App_Info()
        self.commits: List[Commit] = []

    def go(self, **kwargs):
        self.get_appInfo()\
            .commit_popup()\
            .scrollDown_commitPopup(**kwargs)\
            .get_commits()\
            .press_esc()


    def get_appInfo(self) -> App_Info:
        driver = self.driver
        # title
        ele_title = self.__find_element(driver.find_element, By.XPATH, "//*[@itemprop='name']")
        if ele_title:
            self.app_info.name = ele_title.text

        ele_owner = self.__find_element(driver.find_element, By.CSS_SELECTOR, "div.Vbfug.auoIOc")
        if ele_owner:
            self.app_info.owner = self.__get_stringText(ele_owner)

        # 名稱底下的三個小區塊
        ele_underTitle = self.__find_element(driver.find_elements, By.CSS_SELECTOR, "div.wVqUob")
        if ele_underTitle:
            ele_avgRate = self.__find_element(ele_underTitle[0].find_element, By.CSS_SELECTOR, "div.TT9eCd")
            if ele_avgRate:
                self.app_info.avg_rate = self.__get_numericalText(ele_avgRate)

            ele_cntRate = self.__find_element(ele_underTitle[1].find_element, By.CSS_SELECTOR, "div.ClM7O")
            if ele_cntRate:
                self.app_info.downloads = self.__get_stringText(ele_cntRate)
            
            ele_ageCertify = self.__find_element(ele_underTitle[2].find_element, By.CSS_SELECTOR, "div.g1rdde")
            if ele_ageCertify:
                self.app_info.age_certify = self.__get_stringText(ele_ageCertify)
            
        # 最後更新
        ele_lastUpdate = self.__find_element(driver.find_element, By.CSS_SELECTOR, "div.xg1aie")
        if ele_lastUpdate:
            self.app_info.last_update = self.__get_stringText(ele_lastUpdate)
        # 評分的分布
        ele_rankDist = self.__find_element(driver.find_elements, By.CSS_SELECTOR, "div.RutFAf.wcB8se")
        if ele_rankDist:
            self.app_info.rank_dist = [self.__find_numGroup(e.get_attribute("title")) for e in ele_rankDist]
        return self

    def commit_popup(self):
        """
        # 進入評論視窗
        """
        driver = self.driver
        # 所有可點的按鈕的最後一個
        ele_allCommits = self.__find_element(driver.find_elements, By.XPATH, "//button[starts-with(@class, 'VfPpkd-LgbsSe')]")
        if ele_allCommits is not None and len(ele_allCommits)>0:
            ele_allCommits[-1].click()
        return self

    def scrollDown_commitPopup(self, limits = 20, popup_pattern = "//div[@jsname = 'bN97Pc']"):
        """
        在所有評論popup滑到最底下(或達到limits次, 預設20次)
        """
        driver = self.driver
        def __cnt_commits(commitPopup, pattern = "div.RHo1pe"):
            """
            計算現在找到的評論數
            """
            ele_commits = self.__find_element(ele_popup.find_elements, By.CSS_SELECTOR, pattern)
            if ele_commits:
                return len(ele_commits)
            return None

        ele_popup = self.__find_element(driver.find_element, By.XPATH, popup_pattern)
        if ele_popup is None:
            raise ValueError(f"{popup_pattern} not founc.")
  
        new_cnt = __cnt_commits(ele_popup)
        cn_commits = 0
        loop = 0 # "滾到底載入更多" 達到limits次，停止
        stop_times = 0 # 往下捲不一定會觸發"滾到底載入更多"，往下滾5次還碰不到底，就當作真的到底了，停止
        # (如果有滾出新東西 or 雖然沒滾出新東西可是還沒到5次) and (達到設定的"滾到底載入更多"次數)
        while ((new_cnt is not None) and (new_cnt > cn_commits) or (stop_times < 5)) and loop <= limits:
            cn_commits = __cnt_commits(ele_popup) # 往下卷"之前"有多少評論?
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight*1000;', ele_popup)
            new_cnt = __cnt_commits(ele_popup) # 往下卷"之後"有多少評論?
            if new_cnt > cn_commits:
                stop_times = 0
                loop += 1
            else:
                stop_times += 1
        return self

    def press_esc(self):
        # 模擬按下esc (退出評論視窗)
        webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        return self

    def get_commits(self) -> List[Commit]:
        """
        取得目前頁面顯示的所有評論
        """
        # ele.s of all commits
        ele_commits = self.__find_element(self.driver.find_elements, By.CSS_SELECTOR, "div.RHo1pe")
        if ele_commits is None: 
            # 沒有找到評論，下面的都不用做
            return self

        for c in ele_commits:
            cm = Commit()
            ele_author = self.__find_element(c.find_element, By.CSS_SELECTOR, "div.X5PpBb")
            if ele_author:
                cm.author = self.__get_stringText(ele_author)
            ele_rate = self.__find_element(c.find_element, By.CSS_SELECTOR, "div.Jx4nYe > div")
            if ele_rate:        
                cm.rate = self.__find_numGroup(ele_rate.get_attribute('aria-label'))
            ele_date = self.__find_element(c.find_element, By.CSS_SELECTOR, "div.Jx4nYe > span")
            if ele_date:
                cm.date = ele_date.text
            ele_text = self.__find_element(c.find_element, By.CSS_SELECTOR, "div.h3YV2d")
            if ele_text:
                cm.text = ele_text.text
            ele_likes = self.__find_element(c.find_element, By.CSS_SELECTOR, "div > div.AJTPZc")
            if ele_likes:
                cm.likes = self.__find_numGroup(ele_likes.text)
            self.commits.append(cm)
           

        return self

    def __find_element(self, driver_method, by, pattern, **kwargs):
        try:
            ele = driver_method(by, pattern)
            return ele
        except:
            return None

    def __find_numGroup(self, text, groupid = 0) -> Optional[float]:
        if mat := re.search('([0-9.]+)', text):
            return float(mat.group(groupid))
        return None

    def __get_numericalText(self, ele, groupid = 0) -> Optional[float]:
        return self.__find_numGroup(ele.text, groupid = groupid)
    
    def __get_stringText(self, ele, groupid = 0) -> Optional[str]:
        if mat := re.search('([\w ]+)?', ele.text):
            return mat.group(0)
        return None 

# %%
if __name__ == '__main__':
    # 如果 headless = True, 不顯示webdriver視窗
    driver = InitDriver(headless = False)
    # 指定app的網址
    url = 'https://play.google.com/store/apps/details?id=com.hilai.hilaifoods'
    
    # 宣告一個實例
    app1 = app_detail(url = url, driver = driver)

    # 簡易執行
    app1.go()
    
# %%
    # 結果: 店家資訊
    app1.app_info
    type(app1.app_info)
    app1.app_info.name # 用屬性值來取得資料
    app1.app_info.to_dict() # 也可以先轉成dict
    # 結果: 評論
    app1.commits
    # 轉成List[dict]
    [c.to_dict() for c in app1.commits]

    # ---------------------------------------------- #
    # 也可以分步驟執行
    # ---------------------------------------------- #
    # 取得店家資訊的method
    app1.get_appInfo()
    
    # 展開評論popup視窗
    app1.commit_popup()

    # 評論視窗一開始不會顯示所有評論，所以要往下滑展開, 可以用limits來限制滑到底的次數，預設為20(或先到底) 
    #   i.e. 如果20次不夠，請將limits設更大些，例如30
    app1.scrollDown_commitPopup(limits = 1)

    # 抓取所有評論:
    app1.get_commits()
    # 退出評論popup視窗
    app1.press_esc()

# %%
len(app1.commits)

# %%
ele_popup = driver.find_element(By.XPATH, "//div[@jsname = 'bN97Pc']")

cn_commits = 0
loop = 0
while new_cnt is not None and new_cnt > cn_commits and loop <= limits:
    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight*1000;', ele_popup)
            