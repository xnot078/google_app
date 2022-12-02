# %%
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import time, random, re, datetime, os

from typing import Optional, List
from dataclasses import dataclass


def InitDriver(webdrive_path = './chromedriver.exe',
			   incognito = True, 
			   headless = True):
    chrome_options = Options()
    # chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    if incognito:
    	chrome_options.add_argument("incognito")
    if headless:
    	chrome_options.add_argument("--headless")
    Driver = webdriver.Chrome(r"C:\selenium_driver\chrome\chromedriver.exe", chrome_options = chrome_options)
    Driver.implicitly_wait(0.5)
    return Driver

@dataclass
class App_Info:
    name: Optional[str] = None
    owner: Optional[str] = None
    avg_rate: Optional[float] = None
    cnt_rate: Optional[float] = None
    age_certify: Optional[str] = None
    last_update: Optional[str] = None
    rank_dist: List[float] = None


@dataclass
class Commit:
    author: Optional[str] = None
    rate: Optional[float] = None
    date: Optional[str] = None
    text: Optional[str] = None
    likes: Optional[float] = None


driver = InitDriver(headless = False)
url = 'https://play.google.com/store/apps/details?id=com.hilai.hilaifoods'
class app_detail():
    
    def __init__(self,
                 driver: webdriver.chrome.webdriver.WebDriver, 
                 url: str):
        self.driver = driver
        self.driver.get(url)

    def get_appInfo(driver) -> App_Info:
        app_info = App_Info()
        # title
        app_info.name = self.__get_stringText(driver.find_element_by_xpath("//*[@itemprop='name']"))
        app_info.owner = self.__get_stringText(driver.find_element_by_css_selector("div.Vbfug.auoIOc"))
        # 名稱底下的三個小區塊
        ele_underTitle = driver.find_elements_by_css_selector("div.wVqUob")
        app_info.avg_rate = self.__get_numericalText(ele_underTitle[0].find_element_by_css_selector("div.TT9eCd"))
        app_info.cnt_rate = self.__get_stringText(ele_underTitle[1].find_element_by_css_selector("div.ClM7O"))
        app_info.age_certify = self.__get_stringText(ele_underTitle[2].find_element_by_css_selector("div.g1rdde"))
        # 最後更新
        app_info.last_update = self.__get_stringText(driver.find_element_by_css_selector("div.xg1aie"))
        # 評分的分布
        ele_rankDist = driver.find_elements_by_css_selector("div.RutFAf.wcB8se")
        app_info.rank_dist = [self.__find_numGroup(e.get_attribute("title")) for e in ele_rankDist]
        return app_info

    def get_commits(driver) -> :List[Commit]:
        # 進入評論視窗
        ele_allCommits = driver.find_element_by_xpath("//*[@id='ow66']/section/div/div/div[5]/div/div/button")
        ele_allCommits.click()

        # ele.s of all commits
        commits = driver.find_elements_by_css_selector("div.RHo1pe")
        holder = []
        for c in commits:
            cm = Commit()
            cm.author = self.__get_stringText(c.find_element_by_css_selector("div.X5PpBb"))
            ele_rate = c.find_element_by_css_selector("div.Jx4nYe > div")\
                        .get_attribute('aria-label')
            cm.rate = self.__find_numGroup(ele_rate)
            cm.date = c.find_element_by_css_selector("div.Jx4nYe > span").text
            cm.text = c.find_element_by_css_selector("div.h3YV2d").text
            ele_likes = c.find_element_by_xpath("//div[@jscontroller='SWD8cc']")\
                         .get_attribute("data-original-thumbs-up-count")
            cm.likes = self.__find_numGroup(ele_likes)
            holder.append(cm)

        # 退出評論視窗
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        return holder


        
    def __find_numGroup(text, groupid = 0) -> Optional[float]:
        if mat := re.search('([0-9.]+)', text):
            return float(mat.group(groupid))
        return None

    def __get_numericalText(ele, groupid = 0) -> Optional[float]:
        return self.__find_numGroup(ele.text, groupid = groupid)

    def __get_stringText(ele, groupid = 0) -> Optional[str]:
        if mat := re.search('([\w ]+)?', ele.text):
            return mat.group(0)
        return None 
    pass
	
# %%



