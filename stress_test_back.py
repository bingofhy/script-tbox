import json
import random
import string
from locust import HttpUser, TaskSet, task, between

def generate_random_username(length=10):
    """生成随机用户名"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class UserBehavior(TaskSet):
    
    @task
    def register_user(self):
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "authorization": "",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://tboxmn.com",
            "priority": "u=1, i",
            "referer": "https://tboxmn.com/",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        url = "/api/user/register"
        data = {
            "user_string": generate_random_username(),
            "code": "",
            "password": "1234567",
            "re_password": "1234567",
            "extension_code": "fvls",
            "type": "account",
            "payPassword": "1234567",
            "lang": "zh"
        }
        try:
            response = self.client.post(url, headers=headers, data=data)
            print(response.status_code)
            if response.status_code == 200:
                #把data 存储到本地文件 account.csv
                with open('account.csv', 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data) + '\n')
            response = json.loads(response.text)
            print(response)
        except Exception as e:
            print(f"Request failed: {e}")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = "https://ap.tboxmn.com"