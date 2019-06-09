from fdfs_client.client import Fdfs_client

if __name__ ==  '__main__':
    # 创 建一个对象
    client = Fdfs_client('/home/python/myproject/meiduo_mall/meiduo_mall/meiduo_mall/utils/fdfs/client.conf')
    #上传文件
    ret = client.upload_by_filename('/home/python/myproject/meiduo_mall/meiduo_mall/meiduo_mall/static/images/adv02.jpg')
    print(ret)
