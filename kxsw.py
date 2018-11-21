from wsgiref.simple_server import make_server
import requests
import base64
from bs4 import BeautifulSoup
import json
from flask import Flask
from flask import jsonify

app = Flask(__name__)

ssrLink = ''


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    print('我的ssrlink', ssrLink)
    return ssrLink


# @app.route('/hot')
# def hello_flask():
#     root_url = 'http://www.pythontab.com/'
#     return 'hello_flask'

# 往配置文件中写入抓取到的数据


def setData(arrays):
    with open('D:/Document_x64/Downloads/ShadowsocksR-4.7.0/gui-config.json', mode='r+', encoding='utf-8') as file:
        data = json.load(file)
        configs = data['configs']
        # 设置对应信息
        for i in range(len(configs)-1, -1, -1):
            if configs[i]['group'] == 'spider':
                # print(subConfigs['group'])
                configs.pop(i)
        for subSSRObj in arrays:
            ssrInfo = {}
            configs.append(ssrInfo)
            ssrInfo['remarks'] = subSSRObj['server']
            ssrInfo['server'] = subSSRObj['server']
            ssrInfo['server_port'] = subSSRObj['server_port']
            ssrInfo['password'] = subSSRObj['password']
            ssrInfo['method'] = subSSRObj['method']
            ssrInfo['protocol'] = subSSRObj['protocol']
            ssrInfo['obfs'] = subSSRObj['obfs']
            ssrInfo['group'] = 'spider'
            # print(subSSRObj['server'])
        # 保存json数据到文件
    with open("D:/Document_x64/Downloads/ShadowsocksR-4.7.0/gui-config.json", mode="w") as f:
        json.dump(data, f)

# 从ssr网站上获取想应的账号信息


def getSSR():
    url_start = 'https://x.ishadowx.net/'
    global ssrLink
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'}
    response = requests.get(url_start, verify=False, headers=headers)
    if response.status_code == 200:
        ssrArrays, ssrLinkArrays = [], []
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find_all(class_='hover-text')
        for msg in title:
            if not msg.find(id='ipssrc') is None:
                ssrObj, resultSSRLink = getSSRResult('ipssrc', msg)
                ssrArrays.append(ssrObj)
                ssrLinkArrays.append(resultSSRLink)
            elif not msg.find(id='ipssra') is None:
                ssrObj, resultSSRLink = getSSRResult('ipssra', msg)
                ssrArrays.append(ssrObj)
                ssrLinkArrays.append(resultSSRLink)
        # print(ssrArrays)
        for ssrLink in ssrLinkArrays:
            ssrLink = ssrLink+'\n'
            ssrLink = str(base64.b64encode(ssrLink.encode()))[
                2:len(ssrLink)-1]
        print(ssrLink)
        # setData(ssrArrays)

        httpd = make_server('', 8000, application)
        print('Serving HTTP on port 8000...')
        httpd.serve_forever()


# 抓取并转换为ssr地址
def getSSRResult(id, msg):
    ssrObj = {}
    server = msg.find(id=id).string.strip('\n')
    if 'ipssrc' == id:
        server_port = msg.find(id='portssrc').string.strip('\n')
        password = msg.find(id='pwssrc').string.strip('\n')
    elif 'ipssra' == id:
        server_port = msg.find(id='portssra').string.strip('\n')
        password = msg.find(id='pwssra').string.strip('\n')
    method = msg.find_all('h4')[3].string.split(':')[1]  # 加密方法
    strArray = msg.find_all('h4')[4].string.split(' ')
    protocol = strArray[0].lstrip()  # 协议
    obfs = strArray[1].lstrip()  # 混淆
    ssrObj['server'] = server
    ssrObj['server_port'] = server_port
    ssrObj['password'] = password
    ssrObj['method'] = method
    ssrObj['protocol'] = protocol
    ssrObj['obfs'] = obfs
    # 将密码进行base64加密并转化为string
    base64Password = str(base64.b64encode(password.encode()))
    base64Password = base64Password[2:len(base64Password)-1]  # 截取字符串
    # 将拼接出来的地址再次进行base64加密并转化为string
    ssrStr = server+':'+server_port+':'+protocol+':' + \
        method+':'+obfs+':'+base64Password
    base64ssrStr = str(base64.b64encode(ssrStr.encode()))
    resultSSRLink = 'ssr://'+base64ssrStr[2:len(base64ssrStr)-1]
    # print(resultSSRLink)
    return ssrObj, resultSSRLink


if __name__ == '__main__':
    getSSR()
