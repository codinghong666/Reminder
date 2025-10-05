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
- 400MB内存（API模式）

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

#### 配置systemd服务（可选）
```bash
# 复制服务文件
sudo cp src/SDU_DeepSeek/sduapi.service /etc/systemd/system/

# 重新加载配置
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable sduapi.service
sudo systemctl start sduapi.service
```

### 4. 主程序配置

编辑 `src/main/config.env` 文件：

```env
# 模型配置
MODEL=Qwen/Qwen3-8B                    # 本地模型名称
BASE_URL=http://localhost:3001         # LLM API地址（本地或SDU_DeepSeek）

# NapCat配置
TOKEN=your_napcat_token                # NapCat认证token
GROUP_IDS=534116547,914404708         # 监控的QQ群号，用逗号分隔
WORKING_QQ=2372124330                  # 工作QQ号

# 消息配置
MESSAGE_COUNT=5                        # 每次抓取的消息数量
SUMMARY_COUNT=10                       # 摘要生成的消息数量
SEND_ID=1767819342                     # 接收提醒的QQ号

# 时间配置
WORK_TIME=19:35                        # 信息提取时间
SEND_TIME=19:40                        # 提醒发送时间
```

### 5. 服务部署

#### 部署主程序服务
```bash
# 复制服务文件
sudo cp src/main/qqbot.service /etc/systemd/system/

# 修改服务文件中的路径（如需要）
sudo nano /etc/systemd/system/qqbot.service

# 重新加载配置
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable qqbot.service
sudo systemctl start qqbot.service
```

### 6. Flask Web界面

#### 启动Web服务
```bash
cd src/flask
python app.py
```

Web界面将在 `http://localhost:5000` 启动。

#### 功能说明
- **数据查看**: 查看所有抓取的DDL数据
- **数据管理**: 添加、删除DDL记录
- **摘要查看**: 查看AI生成的DDL摘要
- **实时刷新**: 手动刷新数据和摘要

## 服务管理

### 查看运行状态
```bash
# 查看主程序状态
sudo systemctl status qqbot.service

# 查看SDU_DeepSeek状态
sudo systemctl status sduapi.service
```

### 查看实时日志
```bash
# 查看主程序日志
sudo journalctl -u qqbot.service -f

# 查看SDU_DeepSeek日志
sudo journalctl -u sduapi.service -f
```

### 常用管理命令
```bash
# 停止服务
sudo systemctl stop qqbot.service
sudo systemctl stop sduapi.service

# 重启服务
sudo systemctl restart qqbot.service
sudo systemctl restart sduapi.service

# 禁用开机自启
sudo systemctl disable qqbot.service
sudo systemctl disable sduapi.service
```

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
