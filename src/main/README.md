# QQ群聊DDL提醒器

## 项目简介

一个基于NapCat和本地LLM的QQ群聊DDL（截止日期）提醒系统，能够自动抓取群消息、提取DDL信息并定时推送提醒。

## 工作原理

1. **消息抓取**: 使用[NapCat](https://github.com/NapNeko/NapCatQQ)抓取指定QQ群消息
2. **信息提取**: 使用本地LLM提取DDL时间信息
3. **数据存储**: 将提取的信息存储到本地数据库
4. **定时推送**: 每天固定时间扫描数据库，对接近截止日期的DDL进行推送提醒


## 安装配置

### 1. 环境准备

需要至少4gb内存，8gb显存

如果显存不够可以尝试更改参数更小的本地LLM

如果不担心数据泄漏可以使用api

在服务器上配置好 [NapCat](https://github.com/NapNeko/NapCatQQ)

### 2. 配置文件设置

编辑 `config.env` 文件，配置以下参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `TOKEN` | NapCat上的认证token | `1234567890111` |
| `GROUP_IDS` | 需要抓取的群号，多个群用逗号分隔 | `114514,1919810` |
| `MESSAGE_COUNT` | 每天从最新的消息向上抓取的消息条数 | `30` |
| `SEND_ID` | 接收推送消息的QQ号 | `1919810` |
| `WORK_TIME` | 大模型提取信息的时间 | `13:14` |
| `SEND_TIME` | 发送提醒消息的时间 | `5:20` |

**配置文件示例：**
```env
# QQ Bot Configuration
MODEL=Qwen/Qwen3-8B
TOKEN=1234567890111
GROUP_IDS=1062848088
MESSAGE_COUNT=5
SEND_ID=114514
WORK_TIME=2:00
SEND_TIME=8:50

```

### 3. 服务部署

执行以下命令部署systemd服务：

```bash
# 复制服务文件到系统目录
sudo cp /home/coding_hong/Documents/QQBot/main/qqbot.service /etc/systemd/system/

# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable qqbot.service

# 启动服务
sudo systemctl start qqbot.service
```

## 服务管理

### 查看运行状态
```bash
sudo systemctl status qqbot.service
```

### 查看实时日志
```bash
sudo journalctl -u qqbot.service -f
```

### 常用管理命令
```bash
# 停止服务
sudo systemctl stop qqbot.service

# 重启服务
sudo systemctl restart qqbot.service

# 禁用开机自启
sudo systemctl disable qqbot.service
```

## 注意事项

- 确保conda环境RL中已安装所需依赖
- 定期检查日志文件 `minimal_scheduler.log` 和 `send.log`
- 确保NapCat服务正常运行
- 建议在测试环境先验证配置正确性 
