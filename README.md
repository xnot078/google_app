# google_app_commits

取得指定google app在stor中的資訊

## 安裝
1. install:
```
$ pip install git+https://github.com/xnot078/google_app_commits.git
```
2. webdriver:
在[這裡](https://chromedriver.chromium.org/downloads)下載和本機的chrome同版本的webdriver，並解壓縮到安裝的資料夾
(python的資料夾路徑/Lib/site-packages/google_app_commits中)

## 資料:
* app_info:
    - name: app名稱
    - owner: 擁有者
    - avg_rate: 平均評分
    - downloads: 下載次數
    - age_certify: 年齡限制
    - last_update: 更新日期,
    - rank_dist: 評分分布(1, 2, 3, 4, 5各有多少人評分)

* list of commits: 
    (以其中一個commit為例)
    - author: 評論者
    - rate: 評分
    - date: 評論日期
    - text: 評論文本
    - likes: 覺得這則評論有幫助的人數

## 使用:
```python
import google_app_commits as gc

# 如果 headless = True, 不顯示webdriver視窗
driver = gc.InitDriver(headless = False)
# 指定app的網址
url = 'https://play.google.com/store/apps/details?id=com.hilai.hilaifoods'

# 宣告一個實例
app1 = gc.app_detail(url = url, driver = driver)

# 簡易執行
app1.go()
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
```