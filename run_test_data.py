
import random
import time

file = './tboxmn.csv'

# 在 66300到67360 之间生成随机数

while True:
    with open(file, 'a', encoding='utf-8') as f:
        i= random.randint(66300, 67360)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(f"{time_str},{i}\n")
        print(f"{time_str},{i}")
        print('-' * 50)
        time.sleep(1)






