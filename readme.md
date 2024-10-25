# 钛盘相关的文件操作

> 官网：[https://www.tmp.link](https://www.tmp.link)

‍

# 一、已实现功能

* 上传文件到仓库
* 获取优先配额（直链）
* 获取仓库文件列表
* 获取直链文件列表
* 添加直链
* 移除直链

‍

# 二、使用前准备

### 1、钛盘

* 需要有自己的域名，开通直链功能需要
* 需要开通直链功能，具体参考[官网说明](https://bbs.tmp.link/d/563-%E7%9B%B4%E9%93%BE%E8%A6%81%E6%80%8E%E4%B9%88%E6%B7%BB%E5%8A%A0/6)

> 如无法开通，可使用shell脚本来上传文件，需要经常更新 token
>
> [https://github.com/tmplink/tmplink_cli](https://github.com/tmplink/tmplink_cli)

### 2、运行环境

* Python 3.8
* 安装pip依赖

> pip install -r requirements.txt

* 设置环境变量

> // 直链域名
>
> export TMPLINK_MYLINK=[https://xxx.com](https://xxx.com/)
>
> // 钛盘的APIKEY
>
> export TMPLINK_APIKEY=xxxxx

‍

# 三、使用

### 1、上传文件

```bash
# 上传文件到仓库根目录，文件有效期 3 天；返回文件的ukey
python tmplink钛盘.py -u --file /root/abc.log --model 1

# 上传文件到具体目录，文件永久有效，文件夹的mrid可以从钛盘的url中获取；返回文件的ukey
python tmplink钛盘.py -u --file /root/abc.log --mrid xxxx --model 99

# 上传文件到具体目录，文件永久有效，并将该文件添加到直链，会返回url，可直接下载；返回文件的ukey，直链url
python tmplink钛盘.py -u --mylink --file /root/abc.log --mrid xxxx --model 99
```

### 2、获取文件列表

```bash
# 默认获取仓库文件列表
python tmplink钛盘.py -s
# 或者
python tmplink钛盘.py -s --list_of_workspace

# 获取直链文件列表
python tmplink钛盘.py -s --list_of_direct
```

### 3、添加直链

```bash
# 上传文件会返回ukey，获取文件列表时也会反馈ukey，根据ukey来确定唯一文件标识符
# vaild_time 为直链有效期，单位：分钟，默认 1 天，可自行修改代码
python tmplink钛盘.py -l --ukey xxx --vaild_time 60
```

### 4、完整参数

```bash
[root@instance ~]# python tmplink钛盘.py
usage: tmplink钛盘.py [-h] [--quota] [-u] [--mylink] [--file FILE] [--mrid MRID] [--model MODEL] [-l] [--ukey UKEY]
                    [--vaild_time VAILD_TIME] [-d] [--dkey DKEY] [-s] [--list_of_workspace] [--list_of_direct]

上传文件到钛盘，添加文件直链等操作

optional arguments:
  -h, --help            show this help message and exit
  --quota               显示配额信息

上传文件:
  -u, --upload          上传文件
  --mylink              是否添加为直链
  --file FILE           文件的绝对路径
  --mrid MRID           仓库文件夹的mrid
  --model MODEL         文件有效期。默认参数是 2，表示 7 天后过期；0 表示 24 小时；1 表示 3 天；99 表示永久。

添加文件为直链:
  -l, --link            添加文件直链
  --ukey UKEY           文件唯一标识符
  --vaild_time VAILD_TIME
                        直链有效时间，单位：默认 1 天， 0 表示永久有效

删除文件直链:
  -d, --delete          删除文件直链
  --dkey DKEY           直链文件唯一标识符

显示文件列表:
  -s, --show            显示文件列表
  --list_of_workspace   显示仓库文件列表
  --list_of_direct      显示直链文件列表
```

‍
