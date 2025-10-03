# 注意
> 本工具仅供技术研究，使用者应于24小时内删除从山东大学DeepSeek获取的非公开数据。开发者不对任何学术诚信审查问题负责，请优先联系信息化办公室申请官方API权限。
> 本程序不保证您的信息安全，使用者应自行承担风险。请勿将本程序用于非法用途，否则后果自负。
> 开发者不对使用本程序导致的任何问题负责。
> 请勿滥用！！！

# 鸣谢

感谢山东大学数智化支撑研究院（信息办）为山大学子提供的免费DeepSeek服务。

感谢@zeroHYH同学为本程序提供山大统一身份认证的登录支持，使得免于使用网页填表。

# 程序开发宗旨

本程序的目的是为了方便使用DeepSeek的同学，提供一个简单的API接口，方便调用。
网页版没法嵌入到诸如翻译工具或者集成开发环境中，因此开发了这个程序。为了方便同学
能够因地制宜地使用DeepSeek。

# 使用方法

## 使用打包好的程序

直接从 **右边** 的 `Releases` 下载最新版本的程序，解压后运行即可。

在登陆成功后会显示类似的信息：
```bash
INFO:     Started server process [45608]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

第一次启动程序时，会要求输入学号和密码（用于统一身份认证的），登录后会自动保存登录状态（程序所在的目录下会生成cookies.json），下次启动程序时会自动登录。

如果长时间未使用，登录状态可能会过期，此时请手动删除cookies.json文件，然后重新启动程序。

程序将在 `http://localhost:8000` 上运行。

API路径为 /v1/chat/completions，程序不验证密钥，由于原版网页限制，也无法调整参数，因此请直接使用默认参数。

支持以下模型，请在调用工具处填写（严格大小写，如果输入不匹配则默认为DeepSeek+深度思考+联网搜索）：
- deepseek_reasoner_web (DeepSeek+深度思考+联网搜索)
- deepseek_reasoner (DeepSeek+深度思考)
- deepseek_web (DeepSeek+联网搜索)
- deepseek (DeepSeek)
- QwQ (QwQ)
- QwQ_web (QwQ+联网搜索)
- QwQ_reasoner (QwQ+深度思考)
- QwQ_reasoner_web (QwQ+深度思考+联网搜索)

## 从源码运行

您需要这样做，说明您大概率不需要本教程指导