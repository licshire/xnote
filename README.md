# Xnote

[![Build Status](https://travis-ci.org/xupingmao/xnote.svg?branch=master)](https://travis-ci.org/xupingmao/xnote)
[![Coverage Status](https://coveralls.io/repos/github/xupingmao/xnote/badge.svg?branch=master)](https://coveralls.io/github/xupingmao/xnote?branch=master)

xnote是一款致力于提升生活和工作的幸福感的工具，通过将知识库和工具有机结合起来，提供简单好用的个人助理服务。它有如下特点

- 数据统一管理，文章、日志、个人词库以及文件数据N合一
- 可扩展，通过脚本扩展系统功能，监听系统事件完成自定义功能
- 智能搜索，支持搜索知识库、文件系统、工具等等，支持若干语义指令
- 跨平台，既可以在云端部署，也能运行在本地作为系统增强软件


PS：目前本项目主要目标人群是个人，提供有限的多用户支持

![知识库](https://git.oschina.net/xupingmao/xnote/raw/master/screenshots/xnote_home.png)

-----
## 项目地址
- [github](https://github.com/xupingmao/xnote)
- [码云](https://gitee.com/xupingmao/xnote)


## 安装
- 安装python（支持Python2、3，建议Python3）
- 安装依赖的软件包```python -m pip install -r requirements.txt```
- 无需额外配置，初始化的管理员账号是admin/123456
- 启动服务器`python app.py`, 默认1234端口, 浏览器打开http://localhost:1234/ 即可
- 本项目可以直接运行在新浪云应用SAE上面
- 如果启动失败参考 [数据库迁移](./docs/db_migrate.md)

### 启动参数
- `--data {data_path}` 指定数据存储的data目录，比如`python app.py --data D:/data`
- `--port 1234`启动端口号，注意优先使用环境变量{PORT}设置的端口号，这是为了自适应云服务容器的端口
- `--ringtone yes`开启启动语音提醒
- `--delay 60` 延迟启动，单位是秒，这个主要是为了避免重启的定时任务重复执行
- `--useUrlencode yes`针对只支持ASCII编码的文件系统开启urlencode转换非ASCII码字符
- `--initScript {script_name}` 启动时运行指定脚本完成自定义初始化操作


## 功能结构

### 知识库
- Markdown编辑器、可视化编辑器
- 文档分组、标签
- 文档分享
- 搜索


### 日程管理
- 任务清单功能，类似于微博的形式，可以写文字或者上传图片文件等、目前有进行中和完成两个状态
- 日历，日程提醒功能考虑中

### 搜索

搜索提供数据和很多程序的入口，并且支持一些语义化的命令

- [x] 知识库搜索
- [x] 词典检索
- [x] 书籍搜索，搜索`$DATA/books/`目录下的书籍
- [x] 工具搜索，搜索`handlers/tools/`目录下的工具
- [x] 计算简单的数学公式
- [x] 支持一些语义化的功能，比如添加语音提醒，输入 `{30|数字}分钟后提醒我{读书}`,那么30分钟后就会听到电脑姐姐的温馨提醒了^\_^


### 文件管理器
- 需要管理员权限
- 文件列表
- 文件上传下载
- 代码搜索
- 代码行统计

### 定时任务
- 通过配置页面设置执行的脚本和时间匹配规则即可
- 可选的任务包括`handlers/api`目录下的系统API以及`scripts`目录下的自定义脚本
- 自定义脚本支持Python脚本和面向操作系统的原生脚本，包括类Unix的shell脚本和Windows的BAT脚本

 
### 其他工具
- Python文档(pydoc)
- 代码模板
- 文本比较工具(jsdiff)
- 编解码工具(base64,16进制等等)
- 二维码生成器(barcode)
- 语音播报（基于操作系统自带语音助手）
- 天气信息抓取(中国天气网数据)
- 脚本管理器

### 其他特性
- debug模式下自动侦测文件修改并重新加载
- 支持文件下载断点续传,发生网络故障后不用重新下载
- 使用响应式布局，尽量保证PC、移动平台体验一致
- 用户权限，通过Python的装饰器语法，比较方便修改和扩展(见xauth.login\_required)
- 数据库结构自动更新(xtables.py)
- 支持纯ASCII码文件系统（上传文件名会经过urlencode转码）

## 相关文档
- [系统架构](./docs/architecture.md)

## 协议

- GPL

