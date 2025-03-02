import requests
import json
from bs4 import BeautifulSoup

# 读取用户信息
CONFIG_FILE = "config.json"
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("username", ""), config.get("password", "")
    except FileNotFoundError:
        print("⚠️ 配置文件未找到，请创建 config.json 并添加用户名和密码。")
        return "", ""

# 读取配置
USERNAME, PASSWORD = load_config()

# 教务系统 URL
BASE_URL = "https://jw.xmu.edu.cn"
LOGIN_URL = f"{BASE_URL}/login.do"
SSO_LOGIN_URL = "https://ids.xmu.edu.cn/authserver/login?type=userNameLogin"
GRADES_URL = f"{BASE_URL}/xscjcx.do"


def login():
    session = requests.Session()
    
    print("🔄 正在访问教务首页，保持 Session...")
    response = session.get(BASE_URL, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
    print(f"📥 教务首页响应状态码: {response.status_code}")
    
    print("🔄 正在提交初次登录请求...")
    response = session.post(LOGIN_URL, data={"username": USERNAME, "password": PASSWORD}, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
    print(f"📥 登录响应状态码: {response.status_code}")
    
    # 检查是否跳转到SSO统一身份认证
    if "统一身份认证" in response.text or "sso" in response.url:
        print("🔄 发现 SSO 认证，解析登录页面...")
        sso_page = session.get(SSO_LOGIN_URL, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(sso_page.text, 'html.parser')
        
        # 打印 SSO 页面 HTML 代码
        print("🔍 SSO 页面 HTML 代码:", soup.prettify()[:1000])
        
        # 提取所有输入字段
        sso_login_data = {tag["name"]: tag.get("value", "") for tag in soup.find_all("input") if tag.has_attr("name")}
        
        # 添加必要字段
        sso_login_data["username"] = USERNAME
        sso_login_data["password"] = PASSWORD
        sso_login_data["_eventId"] = "submit"
        sso_login_data["lt"] = soup.find("input", {"name": "lt"})["value"] if soup.find("input", {"name": "lt"}) else ""
        sso_login_data["execution"] = soup.find("input", {"name": "execution"})["value"] if soup.find("input", {"name": "execution"}) else ""
        
        # 检查是否需要验证码
        captcha_field = soup.find("input", {"name": "captchaResponse"})
        if captcha_field:
            captcha_value = input("🔒 请输入验证码: ")  # 手动输入验证码
            sso_login_data["captchaResponse"] = captcha_value
        
        print("📤 SSO 登录提交数据:", json.dumps(sso_login_data, indent=2, ensure_ascii=False))
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": SSO_LOGIN_URL,
            "Origin": "https://ids.xmu.edu.cn"
        }
        
        print("🔄 正在提交 SSO 登录请求...")
        response = session.post(SSO_LOGIN_URL, data=sso_login_data, headers=headers, allow_redirects=True)
        print(f"📥 SSO 登录响应状态码: {response.status_code}")
    
    if "logout" in response.text or "退出" in response.text:
        print("✅ 登录成功！")
        return session
    else:
        print("❌ 登录失败，可能需要验证码或额外参数")
        print("服务器返回:", response.text[:500])
        return None

def get_grades(session):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": BASE_URL
    }
    
    print("🔄 正在获取成绩数据...")
    response = session.get(GRADES_URL, headers=headers)
    print(f"📥 成绩查询响应状态码: {response.status_code}")
    
    try:
        data = response.json()
        print("✅ 成绩数据成功解析！")
        return data
    except json.JSONDecodeError:
        print("❌ 服务器返回的不是 JSON 格式，可能未登录或 Session 失效")
        print("返回内容:", response.text[:500])
        return None

if __name__ == "__main__":
    print("🚀 开始执行教务系统爬虫...")
    session = login()
    if session:
        grades = get_grades(session)
        
        if grades:
            print("🎓 成绩数据:", json.dumps(grades, indent=2, ensure_ascii=False))
            with open("grades.json", "w", encoding="utf-8") as f:
                json.dump(grades, f, indent=2, ensure_ascii=False)
            print("💾 成绩数据已保存到 grades.json")
        else:
            print("⚠️ 未能获取成绩数据")