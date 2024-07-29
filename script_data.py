import requests
import time
import os
import concurrent.futures
import threading

# local file
file = './tboxmn.csv'


if not os.path.exists(file):
    with open(file, 'w', encoding='utf-8') as f:
        f.write('time,value\n')

# 
file_lock = threading.Lock()

def get_(authorization):
    headers = {
        "accept": "*/*",
        "accept-language": "en,zh-CN;q=0.9,zh;q=0.8",
        "authorization": authorization,
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://tboxmn.com",
        "priority": "u=1, i",
        "referer": "https://tboxmn.com/",
        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}
    url = "https://ap.tboxmn.com/api/microtrade/payable_currencies"
    params = {
        "lang": "en"
    }
    response = requests.get(url, headers=headers, params=params)
    return response

def fetch_and_write(authorization):
    for _ in range(600):
        response = get_(authorization)
        price = 0
        if response.status_code == 200:
            data = response.json()
            price = data["message"][0]["price"]
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"{time_str} : {price}")
        print('-' * 50)
        with file_lock:
            with open(file, 'a', encoding='utf-8') as f:
                f.write(f"{time_str},{price}\n")
        time.sleep(0.5)

authorization_list = ["0735892b892889e6fd7cf89e75ffff4f","2891321663f2900071828ef552e731bf","66f54cc531848f4b0e847f27da63261b"]  # 你的authorization列表


with concurrent.futures.ThreadPoolExecutor(max_workers=len(authorization_list)) as executor:
    futures = [executor.submit(fetch_and_write, auth) for auth in authorization_list]
    concurrent.futures.wait(futures)