# YOYOTIX 🎫

YOYOTIX 是一個基於 Django 打造的線上活動購票平台，整合會員管理、票券購買、活動展示與客服留言系統，致力於提供使用者順暢、安全的購票體驗。

## 專案架構

```

yoyotix/
├── manage.py
├── db.sqlite3
│
├── yoyotix/                # 專案主設定
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── accounts/               # App 1：會員系統
│   ├── models.py           # 自訂 CustomUser 模型
│   ├── views.py
│   ├── forms.py            # 註冊、自訂欄位驗證
│   ├── urls.py
│   └── templates/accounts/
│       ├── login.html
│       ├── register.html
│       └── profile.html
│
├── tickets/                # App 2：活動票券系統
│   ├── models.py           # Event、Ticket、Order
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/tickets/
│       ├── index.html
│       ├── event\_detail.html
│       └── order\_success.html
│
├── support/                # App 3：客服中心
│   ├── models.py           # Message 模型
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── templates/support/
│       ├── contact\_form.html
│       ├── message\_list.html
│       └── message\_detail.html
│
├── templates/
│   ├── base.html           # 共用母模板
│   └── includes/
│       ├── head.html
│       └── footer.html
│
├── static/
│   └── css/style.css       # 前端樣式

````

## 🔧 核心功能

### 1️ 活動展示
- 首頁呈現所有活動，支援搜尋與類別篩選
- 每場活動有獨立詳情頁：主視覺圖、演出時間、票價、剩餘票數一目了然

### 2️ 購票系統
- 支援開賣時間設定，未開賣活動會顯示提示
- 每人購票上限控制（最多 4 張）
- 剩餘票數即時反映
- 購票流程中設有訂單確認頁，避免誤操作
- 支援取票後顯示 QR Code（含驗票碼）

### 3️ 會員系統
- 使用者註冊 / 登入 / 編輯個人檔案（支援手機與生日欄位驗證）
- 訂單紀錄查詢：查詢每筆票券狀態與訂單詳情

### 4️⃣ 客服留言中心
- 支援匿名或具名留言
- 每則留言可設定「公開 / 非公開」
- 留言詳情頁支援留言追蹤

##  技術與工具

- Python 3.6+
- Django 3.2
- SQLite（可改接 PostgreSQL）
- Bootstrap 5 前端框架
- Django Template Language
- Django Messages Framework
- Django ModelForm 驗證與自訂欄位
- Captcha 驗證碼防機器人註冊
- UUID 與 Hash 驗票機制
- 動態 QR Code 生成（待整合）

## 開發環境安裝

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝套件
pip install -r requirements.txt

# 套用遷移
python manage.py migrate

# 啟動伺服器
python manage.py runserver
````

