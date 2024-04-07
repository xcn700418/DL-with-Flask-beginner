import requests, json, base64

# 将图片转为base64格式的才能进行上传
encoded = base64.b64encode(open(r"/upload/your/image/here", 'rb').read())
decoded = encoded.decode()

url = "your/server/ip" # 输入服务器IP
mydata = {"name":"cat", "imgData":decoded}
mydata = json.dumps(mydata)
headers={"Content-Type": "application/json"}

res = requests.post(url=url, headers=headers, data=mydata)
print("response:", res.text)  # 返回请求结果
