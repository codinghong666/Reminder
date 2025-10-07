# QQ群聊DDL提醒器

## 项目简介
有任何问题可以先查看
[DeepWiki](https://deepwiki.com/codinghong666/Reminder)

一个基于NapCat和本地LLM的QQ群聊DDL（截止日期）提醒系统，能够自动抓取群消息、提取DDL信息并定时推送提醒。支持使用SDU_DeepSeek API或本地LLM进行信息提取，并提供Web界面进行数据管理。

## 项目结构

```
QQBot/Reminder/
├── README.md                    # 项目说明文档
├── src/                         # 源代码目录
│   ├── main/                    # 主要功能模块
│   │   ├── config.env          # 配置文件
│   │   ├── main.py             # 主程序入口
│   │   ├── work.py             # 工作调度模块
│   │   ├── send.py             # 消息发送模块
│   │   ├── summary.py          # 摘要生成模块
│   │   ├── llm.py              # LLM调用模块
│   │   ├── datebase.py         # 数据库操作
│   │   ├── qqbot.service       # systemd服务配置
│   │   └── output/             # 输出目录
│   ├── flask/                   # Web界面
│   │   ├── app.py              # Flask应用
│   │   ├── templates/          # HTML模板
│   │   │   └── index.html      # 主页面
│   │   └── static/             # 静态资源
│   │       ├── css/styles.css  # 样式文件
│   │       └── js/app.js       # JavaScript文件
│   ├── SDU_DeepSeek/           # SDU DeepSeek API
│   │   ├── main.py             # API服务入口
│   │   ├── sduapi.service      # systemd服务配置
│   │   ├── sduwrap.py          # API封装
│   │   └── cookies.json        # 登录状态（自动生成）
│   └── requirements.txt        # Python依赖
├── scripts/                     # 实用脚本
│   └── generate_services.sh     # 自动生成并安装 systemd 单元
```

## 工作原理

1. **消息抓取**: 使用[NapCat](https://github.com/NapNeko/NapCatQQ)抓取指定QQ群消息
2. **信息提取**: 使用SDU_DeepSeek API或本地LLM提取DDL时间信息
3. **数据存储**: 将提取的信息存储到本地SQLite数据库
4. **定时推送**: 每天固定时间扫描数据库，对接近截止日期的DDL进行推送提醒
5. **Web管理**: 通过Flask Web界面查看和管理DDL数据

## 安装配置

### 1. 环境准备

#### 系统要求
- 至少4GB内存（本地LLM模式需要8GB显存）
- 50MB内存（API模式）

### 2. NapCat配置

#### 安装NapCat
1. 下载[NapCat](https://github.com/NapNeko/NapCatQQ)最新版本
2. 解压到合适目录
3. 运行NapCat并获取认证token

#### 配置NapCat
- 启动NapCat后，在Web界面获取API token
- 记录token用于后续配置

### 3. SDU_DeepSeek配置（可选）

如果您是山东大学学生，可以使用SDU_DeepSeek API：

#### 启动SDU_DeepSeek服务
```bash
cd src/SDU_DeepSeek
python main.py
```

首次运行会要求输入学号和密码，登录成功后会自动保存登录状态。



### 4. 主程序配置

编辑 `src/main/config.env` 文件：

```env
# 模型配置
MODEL=Qwen/Qwen3-8B                    # 本地/远程模型名称
BASE_URL=http://localhost:3000        # LLM/API 基础地址（本地或SDU_DeepSeek）

# 模式选择
MODEL_CHOICE=api_model                 # 可选：local_model | sdu_model | api_model

# NapCat配置
TOKEN=napcat_token_888888              # NapCat认证token（示例）
GROUP_IDS=888888888,666666666          # 监控的QQ群号（示例，用逗号分隔）
WORKING_QQ=1008611                     # 工作QQ号（示例）

# 消息配置
MESSAGE_COUNT=5                        # 每次抓取的消息数量
SUMMARY_COUNT=5                        # 摘要生成的消息数量
SEND_ID=10086                          # 接收提醒的QQ号（示例）

# 时间配置
WORK_TIME=19:35                        # 信息提取时间（24小时制）
SEND_TIME=19:40                        # 提醒发送时间（24小时制）

# API密钥
API_KEY=sk-****-8888-6666-168-1314     # LLM/API密钥（示例占位）
```

### 5. 服务部署（自动）

#### 使用脚本一键生成并安装 systemd 服务
```bash
#### 配置systemd服务（可选，推荐用脚本自动生成路径）
```bash
# 授权脚本（首次）
chmod +x scripts/generate_services.sh

#查看当前python版本
which python

# 可选：指定 Python 解释器与自动启动
# 使用你自己的 Python 路径（如 /home/you/miniconda3/envs/qqbot/bin/python）
PYTHON_BIN=/usr/bin/python3 AUTO_START=1 sudo -E scripts/generate_services.sh
```
```

脚本会根据当前仓库路径自动生成并写入：
- `qqbot.service`（工作目录：`src/main`，启动 `main.py`）
- `sduapi.service`（工作目录：`src/SDU_DeepSeek`，启动 `main.py`）

常用操作：
```bash
sudo systemctl daemon-reload
sudo systemctl enable qqbot.service && sudo systemctl restart qqbot.service
sudo systemctl enable sduapi.service && sudo systemctl restart sduapi.service
watch -n 1 sudo systemctl status qqbot.service
```

### 6. Flask Web界面

#### 启动Web服务
```bash
cd src/flask
python app.py
```

Web界面将在 `http://localhost:5678` 启动。

#### 功能说明
- **数据查看**: 查看所有抓取的DDL数据
- **数据管理**: 添加、删除DDL记录
- **摘要查看**: 查看AI生成的DDL摘要
- **实时刷新**: 手动刷新数据和摘要


## 使用说明

### 1. 启动所有服务
```bash
# 启动SDU_DeepSeek（如果使用）
sudo systemctl start sduapi.service

# 启动主程序
sudo systemctl start qqbot.service

# 启动Web界面（可选）
cd src/flask && python app.py
```

### 2. 访问Web界面
打开浏览器访问 `http://localhost:5000` 进行数据管理。

### 3. 查看日志
定期检查日志文件确保服务正常运行：
- `src/main/minimal_scheduler.log` - 调度器日志
- `src/main/send.log` - 发送日志

## 注意事项

- 确保所有服务正常运行
- 定期检查日志文件
- 确保NapCat服务正常运行
- SDU_DeepSeek需要定期重新登录（删除cookies.json文件）
- 建议在测试环境先验证配置正确性
- 使用本地LLM时注意显存使用情况
