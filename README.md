![img](./logo/png/logo-title.png)

<h3><div align="center">Telegram 转发器 | Telegram Forwarder</div>

---

<div align="center">

[![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)][docker-url] [![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-4CAF50?style=flat-square)](https://github.com/Heavrnl/TelegramForwarder/blob/main/LICENSE)

[docker-url]: https://hub.docker.com/r/heavrnl/telegramforwarder

</div>

## 简介
Telegram 转发器是一个消息转发工具，只需要你的账号加入频道/群聊即可以将指定聊天中的消息转发到其他聊天，不需要bot也加入。可用于**信息流整合过滤**，**消息提醒**，**内容收藏**等多种场景。

- 🔄 **多源转发**：支持从多个来源转发到指定目标
- 🔍 **关键词过滤**：支持白名单和黑名单模式
- 📝 **正则匹配**：支持正则表达式匹配目标文本
- 📋 **内容修改**：支持多种方式修改消息内容
- 🤖 **AI 处理**：支持使用 AI 处理消息内容
- 🔗 **联动同步**：支持与[通用论坛屏蔽插件](https://github.com/heavrnl/universalforumblock)联动同步，实现三端屏蔽

## 快速开始

### 1. 准备工作

1. 获取 Telegram API 凭据：
   - 访问 https://my.telegram.org/apps
   - 创建一个应用获取 `API_ID` 和 `API_HASH`

2. 获取机器人 Token：
   - 与 @BotFather 对话创建机器人
   - 获取机器人的 `BOT_TOKEN`

3. 获取用户 ID：
   - 与 @userinfobot 对话获取你的 `USER_ID`

### 2. 配置环境

新建文件夹
```bash
mkdir ./TelegramForwarder && cd ./TelegramForwarder
```
新建`.env`文件，填写参数，或者直接下载仓库的`.env.example`文件
```bash
wget https://raw.githubusercontent.com/Heavrnl/TelegramForwarder/refs/heads/main/.env.example -O .env
```
```ini
# Telegram API 配置 (从 https://my.telegram.org/apps 获取)
API_ID=
API_HASH=

# 用户账号登录用的手机号 (格式如: +8613812345678)
PHONE_NUMBER=

# Bot Token
BOT_TOKEN=

# 用户ID (从 @userinfobot 获取)
USER_ID=

# 最大媒体文件大小限制（单位：MB），不填或0表示无限制
MAX_MEDIA_SIZE=15

# 是否开启调试日志 (true/false)
DEBUG=false

# 数据库配置
DATABASE_URL=sqlite:///./db/forward.db

# UI 布局配置
AI_MODELS_PER_PAGE=10
KEYWORDS_PER_PAGE=10


# 默认AI模型
DEFAULT_AI_MODEL=gemini-2.0-flash

# OpenAi API Key
# 留空使用官方接口 https://api.openai.com/v1
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=  

# Claude API Key
# 默认使用官方接口
CLAUDE_API_KEY=your_claude_api_key

# Gemini API Key
# 默认使用官方接口
GEMINI_API_KEY=your_gemini_api_key

# DeepSeek API Key
# 留空使用官方接口 https://api.deepseek.com/v1
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=  

# Qwen API Key
# 留空使用官方接口 https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=your_qwen_api_key
QWEN_API_BASE=  

# Grok API Key
# 留空使用官方接口 https://api.x.ai/v1
GROK_API_KEY=your_grok_api_key
GROK_API_BASE=     

# 默认AI提示词
DEFAULT_AI_PROMPT=请将以下内容翻译成自然流畅的中文，除此之外不需要更改任何内容。

# 默认AI总结提示词
DEFAULT_SUMMARY_PROMPT=请总结以下频道/群组24小时内的消息。
# 默认总结时间
DEFAULT_SUMMARY_TIME=07:00
# 默认时区
DEFAULT_TIMEZONE=Asia/Shanghai


######### 扩展内容 #########

# 是否开启与通用论坛屏蔽插件服务端的同步服务 (true/false)
UFB_ENABLED=false
# 服务端地址
UFB_SERVER_URL=
# 用户API
UFB_TOKEN=

```

新建 `docker-compose.yml` 文件，内容如下：

```yaml
services:
  telegram-forwarder:
    image: heavrnl/telegramforwarder:latest
    container_name: telegram-forwarder
    restart: unless-stopped
    volumes:
      - ./db:/app/db
      - ./.env:/app/.env
      - ./sessions:/app/sessions
      - ./temp:/app/temp
      - ./ufb/config:/app/ufb/config
      - ./config:/app/config
    stdin_open: true
    tty: true
```

### 3. 启动服务

首次运行（需要验证）：

```bash
docker-compose run -it telegram-forwarder
```
CTRL+C 退出容器

修改 docker-compose.yml 文件，修改 `stdin_open: false` 和 `tty: false`

后台运行：
```bash
docker-compose up -d
```


## 使用示例

假设订阅了频道 "TG 新闻" (https://t.me/tgnews) 和 "TG 阅读" (https://t.me/tgread) ，但想过滤掉一些不感兴趣的内容：

1. 创建一个 Telegram 群组/频道（例如："My TG Filter"）
2. 将机器人添加到群组/频道，并设置为管理员
3. 在**新创建**的群组/频道中发送命令：
   ```bash
   /bind https://t.me/tgnews 或者 /bind "TG 新闻"
   /bind https://t.me/tgread 或者 /bind "TG 阅读"
   ```
4. 设置消息处理模式：
   ```bash
   /settings
   ```
   选择要操作的对应频道的规则，根据喜好设置
   
   特别说明：
   - 如果对消息需要进行二次中转处理，可以开启`删除原消息`
   - 预览模式：开启后，会对消息第一条链接进行预览
   ![img](./images/settings_main.png)

5. 添加屏蔽关键词：
   ```bash
   /add 广告 推广 '这是 广告'
   ```

6. 如果发现转发的消息格式有问题（比如有多余的符号），可以使用正则表达式处理：
   ```bash
   /replace \*\*
   ```
   这会删除消息中的所有 `**` 符号

>注意：以上增删改查操作，只对第一个绑定的规则生效，示例里是TG 新闻。若想对TG 阅读进行操作，需要先使用`/settings(/s)`，选择TG 阅读，再点击"应用当前规则"，就可以对此进行增删改查操作了。也可以使用`/add_all(/aa)`，`/replace_all(/ra)`等指令同时对两条规则生效

这样，你就能收到经过过滤和格式化的频道消息了

### AI设置相关

项目提供了AI处理接口,可以对消息进行智能化处理。配合提示词可以应用多种场景例如：
- 翻译
- 总结
- 自动对内容打标签
- 智能去除广告
- ............

在settings中点击`AI设置`即可进入设置菜单。每条转发规则都可以独立配置AI处理。

需要在`.env`文件中配置AI相关参数, 如API_KEY, API_BASE(API_BASE为可选项目, 默认使用官方接口)等

主要设置项说明:

- **AI处理**: 开启后将匹配规则的消息发送到AI模型进行处理
- **AI模型**: 
  - 点击切换使用的AI模型
  - 默认使用`.env`中配置的模型
  - 可在`config/ai_models.txt`中自定义可选模型列表
- **AI提示词**:
  - 点击修改处理消息的提示词
  - 默认使用`.env`中的提示词
  - 开启AI处理后按提示词处理消息
- **AI总结**:
  - 开启后在指定时间总结24小时内的消息
  - 将总结结果发送到目标聊天
  - 注意:此功能消耗较多API token
- **总结时间**:
  - 可在`config/summary_time.txt`中设置列表,格式为`HH:MM`，如`07:00`表示每天早上7点总结
  - 可在`.env`中设置默认时间和时区
- **AI总结提示词**:
  - 点击修改总结的提示词
  - 默认使用`.env`中的提示词

![img](./images/settings_ai.png)

---

### 特殊案例
TG频道的部分消息由于文字嵌入链接，点击会让你确认再跳转，例如nodeseek的官方通知频道

频道的原始消息格式
```
[**贴子标题**](https://www.nodeseek.com/post-xxxx-1)
```

可以对通知频道的转发规则**依次**使用以下指令
```
/replace \*\*
/replace \[(?:\[([^\]]+)\])?([^\]]+)\]\(([^)]+)\) [\1]\2\n(\3)
/replace \[\]\s*
```
最后所有转发过来的消息都会变成以下格式，这样直接点击链接就无需确认跳转了

```
贴子标题
(https://www.nodeseek.com/post-xxxx-1)
```
---


### 设置说明

转发模式分为两种:

1. **用户模式**
   - 消息转发最完整，保留原始格式
   - 需要频道/群聊没有限制转发
   - 由于是自身发送消息，无法收到通知提醒
   - 可以使用另一个 Telegram 账号来登录我们的程序，这样主账号就能收到通知

2. **机器人模式** 
	- **不需要机器人进入相关的频道/群聊，只需要机器人在你新建的频道/群聊即可**
   - 自定义程度最高，可灵活设置转发规则
   - 部分复杂消息可能需要用 `/replace` 命令调整格式
   - 可以正常接收消息通知

建议根据实际需求选择合适的模式。如果注重消息完整性，选择用户模式；如果需要更多自定义功能和通知提醒，选择机器人模式。


### 扩展内容

####  与通用论坛屏蔽插件联动
> https://github.com/heavrnl/universalforumblock

确保.env文件中已配置相关参数，在已经绑定好的聊天窗口中使用`/ufb_bind <论坛域名>`，即可实现三端联动屏蔽，使用`/ufb_item_change`切换要同步当前域名的主页关键字/主页用户名/内容页关键字/内容页用户名

## 完整指令, 支持缩写

```bash
绑定转发 
/bind(/b) <目标聊天链接或名称> - 名称用引号包裹

关键字管理
/add(/a) <关键字1> [关键字2] ... - 添加普通关键字到当前规则
/add_regex(/ar) <正则1> [正则2] ... - 添加正则表达式关键字到当前规则
/add_all(/aa) <关键字1> [关键字2] ... - 添加普通关键字到所有规则
/add_regex_all(/ara) <正则1> [正则2] ... - 添加正则表达式关键字到所有规则
/import_keyword(/ik) <同时发送文件> - 指令和文件一起发送，一行一个关键字
/import_regex_keyword(/irk) <同时发送文件> - 指令和文件一起发送，一行一个正则表达式
/export_keyword(/ek) - 导出当前规则的关键字到文件

替换规则
/replace(/r) <匹配模式> <替换内容/替换表达式> - 添加替换规则到当前规则
/replace_all(/ra) <匹配模式> <替换内容/替换表达式> - 添加替换规则到所有规则
/import_replace(/ir) <同时发送文件> - 指令和文件一起发送，一行一个替换规则
/export_replace(/er) - 导出当前规则的替换规则到文件
注意：不填替换内容则删除匹配内容

切换规则
- 在settings中切换当前操作的转发规则

查看列表
/list_keyword(/lk) - 查看当前规则的关键字列表
/list_replace(/lr) - 查看当前规则的替换规则列表

设置管理
/settings(/s) - 显示选用的转发规则的设置

UFB
/ufb_bind(/ub) <域名> - 绑定指定的域名
/ufb_unbind(/ub) - 解除域名绑定
/ufb_item_change(/uc) - 指定绑定域名下的项目

清除数据
/clear_all(/ca) - 清空所有数据
```

## 捐赠

如果你觉得这个项目对你有帮助，欢迎通过以下方式请我喝杯咖啡：

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/0heavrnl)


## 开源协议

本项目采用 [GPL-3.0](LICENSE) 开源协议，详细信息请参阅 [LICENSE](LICENSE) 文件。
