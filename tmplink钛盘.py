# coding:UTF-8
# @Author        :   ChenDY2233
# @Time          :   2024-10-17 09:27
# @Software      :   VS Code
# @Description   :   上传文件到钛盘，添加文件直链等操作
# @OfficalSite   :   https://www.tmp.link/

import requests
import os
import json
import traceback
import argparse


root_dir = os.path.abspath(os.path.dirname(__file__))
# os.chdir(root_dir)


def init():
    """
    初始化参数
    :return:
    """
    global tmplink_apikey, tmplink_mylink
    tmplink_apikey = os.getenv('TMPLINK_APIKEY')  # 钛盘API密钥
    tmplink_mylink = os.getenv('TMPLINK_MYLINK')  # 钛盘直链域名

    if not tmplink_apikey or not tmplink_mylink:
        print('请设置环境变量 TMPLINK_APIKEY 和 TMPLINK_MYLINK')
        exit()


def main():
    """
    主函数
    :return:
    """
    parser = argparse.ArgumentParser(description='上传文件到钛盘，添加文件直链等操作')
    parser.add_argument('--quota', help='显示配额信息', action='store_true')
    
    # 上传文件参数
    upload_group = parser.add_argument_group('上传文件')
    upload_group.add_argument('-u', '--upload', help='上传文件', action='store_true')
    upload_group.add_argument('--mylink', help='是否添加为直链', action='store_true')
    upload_group.add_argument('--file', help='文件的绝对路径', type=str)
    upload_group.add_argument('--mrid', help='仓库文件夹的mrid', type=str)
    upload_group.add_argument('--model', help='文件有效期。默认参数是 2，表示 7 天后过期；0 表示 24 小时；1 表示 3 天；99 表示永久。', type=str)

    # 添加文件为直链
    link_group = parser.add_argument_group('添加文件为直链')
    link_group.add_argument('-l', '--link', help='添加文件直链', action='store_true')
    link_group.add_argument('--ukey', help='文件唯一标识符', type=str)
    link_group.add_argument('--vaild_time', help='直链有效时间，单位：默认 1 天， 0 表示永久有效', type=int, required=False, default=60*24)

    # 删除文件直链
    delete_group = parser.add_argument_group('删除文件直链')
    delete_group.add_argument('-d', '--delete', help='删除文件直链', action='store_true')
    delete_group.add_argument('--dkey', help='直链文件唯一标识符', type=str)

    # 显示文件列表
    show_group = parser.add_argument_group('显示文件列表')
    show_group.add_argument('-s', '--show', help='显示文件列表', action='store_true')
    show_group.add_argument('--list_of_workspace', help='显示仓库文件列表', required=False, action='store_true')
    show_group.add_argument('--list_of_direct', help='显示直链文件列表', required=False, action='store_true')

    # 解析参数
    args = parser.parse_args()

    if args.upload:
        init()
        # upload_file(args.upload)
        if not args.file:
            print('请指定文件路径')
            exit()
        if not os.path.exists(args.file):
            print('文件不存在')
            exit()
        ukey = upload_file(args.file, args.mrid, args.model)
        if args.mylink:
            link_add(ukey)
    elif args.link:
        init()
        if not args.ukey:
            print('请指定文件唯一标识符')
            exit()
        link_add(args.ukey, args.vaild_time)
    elif args.delete:
        init()
        if not args.dkey:
            print('请指定直链文件唯一标识符')
            exit()
        link_del(args.dkey)
    elif args.show:
        init()
        if args.list_of_direct:
            get_filelist('list_of_direct')
        else:
            get_filelist('list_of_workspace')
    elif args.quota:
        init()
        get_quota()
    else:
        parser.print_help()


def get_filelist(action : str = 'list_of_workspace') -> list:
    """
    获取钛盘文件列表
    :param action : list_of_workspace/list_of_direct
    :return: 文件列表
    """
    filelist = []
    try:
        url = 'https://tmp-api.vx-cdn.com/services/direct'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'key': tmplink_apikey,
            'action': action,
            'page': '1'
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            result = json.loads(response.text)
            if result['status'] == 1:
                filelist = result['data']
            elif result['status'] == 0:
                pass
                # print('文件列表为空：', result)
            else:
                print('返回异常：', result)
    except Exception as e:
        traceback.print_exc()
    finally:
        list_type = '仓库' if action == 'list_of_workspace' else '直链'
        print(f'{list_type}文件列表：')
        print(json.dumps(filelist, indent=2, ensure_ascii=False))
        return filelist


def get_quota() -> dict:
    """
    获取钛盘配额信息
    :return: 配额信息，单位：字节 Byte
    """
    result = {'quota': 0}
    try:
        url = 'https://tmp-api.vx-cdn.com/services/direct'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'key': tmplink_apikey,
            'action': 'quota'
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            res = json.loads(response.text)
            if res['status'] == 1:
                result = res['data']
            elif res['status'] == 0:
                # 配额信息为空
                pass
                # print('获取配额信息失败：', res)
            else:
                pass
                # print('返回异常：', res)
    except Exception as e:
        traceback.print_exc()
    finally:
        print('配额信息：', '{:.2f} GB'.format(result['quota']/1024/1024/1024))
        return result


def link_add(ukey:str = '', vaild_time:int = 60*24) -> str:
    """
    添加文件直链
    :param ukey: 文件唯一标识符
    :param vaild_time: 直链有效时间，单位：默认 1 天， 0 表示永久有效
    :return: 直链地址
    """
    try:
        vaild_time = 60*24 if not vaild_time else vaild_time
        url = 'https://tmp-api.vx-cdn.com/services/direct'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'key': tmplink_apikey,
            'action': 'link_add',
            'ukey': ukey,
            'vaild_time': vaild_time
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            res = json.loads(response.text)
            # print(res)
            if res['status'] == 1:
                # 直链添加成功
                linear = f'{tmplink_mylink}/files/{res["data"][0]["dkey"]}/{res["data"][0]["name"]}'
                print(f'直链地址：{linear}')
                print(f'文件唯一标识符dkey：{res["data"][0]["dkey"]}')
                print(f'有效期：{vaild_time} 分钟')
                return res
            elif res['status'] == 0:
                print('添加直链失败：', res)
            elif res['status'] == 1001:
                print('文件不存在：', res)
            elif res['status'] == 1002:
                print('内部错误：', res)
            else:
                print('返回异常：', res)
    except Exception as e:
        traceback.print_exc()


def link_del(dkey:str = '', delete:bool = False) -> str:
    """
    删除文件直链
    :param dkey: 直链文件唯一标识符
    :param delete: 是否同时删除文件，如果设定为 true，将删除对应的文件，其它设定为此文件的直链也会一同删除。默认为 false。
    :return: 删除结果
    """
    try:
        url = 'https://tmp-api.vx-cdn.com/services/direct'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'key': tmplink_apikey,
            'action': 'link_del',
            'dkey': dkey,
            'delete': delete
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            res = json.loads(response.text)
            # {'data': 'None', 'status': 1, 'debug': []}
            print(res)
            if res['status'] == 1:
                print('直链删除成功')
                return res
            elif res['status'] == 0:
                print('删除直链失败：', res)
            elif res['status'] == 1003:
                print('没有找到对应的直链：', res)
            else:
                print('返回异常：', res)
    except Exception as e:
        traceback.print_exc()


def upload_file(filepath:str = '', mrid:str = None, model:str = '2') -> str:
    """
    上传文件到钛盘
    :param filepath: 文件路径
    :param mrid: 文件夹 ID。可选参数，设定此参数之后，文件将会被上传到指定文件夹。不设置此参数，文件将会被上传到仓库。
    :param model: 文件有效期。默认参数是 2，表示 7 天后过期；0 表示 24 小时；1 表示 3 天；99 表示永久。
    :return: 文件唯一标识符

    :res 
        1 : 上传完成，此时返回的 Data 数据为文件的 UKEY。
        0 : 上传失败，无效的请求。
        2 : 上传失败，文件大小超出了限制。
        3 : 上传失败，服务器繁忙，无法处理此次请求。
        4 : 上传失败，私有空间不足，无法存储文件。
        5 : 上传失败，目前上传的文件总量已经超出了当日配额。存储至私有空间时不受限制。
        6 : 上传失败，API Key 已失效。
    """
    try:
        if not os.path.exists(filepath):
            print(f'文件不存在：{filepath}')
            return None
        model = '2' if not model else model
        url = 'https://tmp-cli.vx-cdn.com/app/upload_cli'
        data = {
            'key': tmplink_apikey,
            'mrid': mrid,
            'model': model
        }
        files = {
            'file': open(filepath, 'rb')
        }
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            res = json.loads(response.text)
            res_str = json.dumps(res, indent=2, ensure_ascii=False)
            if res['status'] == 1:
                print('文件上传成功ukey：', res['data'])
                return res['data']
            elif res['status'] == 0:
                print('文件上传失败：')
            elif res['status'] == 2:
                print('文件大小超出了限制：')
            elif res['status'] == 3:
                print('服务器繁忙，无法处理此次请求：')
            elif res['status'] == 4:
                print('私有空间不足，无法存储文件：')
            elif res['status'] == 5:
                print('目前上传的文件总量已经超出了当日配额。存储至私有空间时不受限制：')
            elif res['status'] == 6:
                print('API Key 已失效：')
            else:
                print('返回异常：')
            print(res_str)
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    main()
