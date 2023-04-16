# 把 vits 的 tts 封装成API接口, 用于语音合成

## 用法

把 Dockerfile 放到 vits 的根目录下, 然后把模型文件放到 tts_web_api/model/{模型名} 目录下, 然后执行:  

```bash
docker build -t tts_web_api .
docker run -d -p 80:3232 tts_web_api
```

# tts_web_api/model/{模型名} 文件要有
* G_latest.pth
* moegoe_config.json

如果要用清华源来安装 python 包, 请把 `Dockerfile` 这一行该下
```
RUN pip3 install -r requirements.txt
```
改成
```
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
