from fdfs_client.client import Fdfs_client

if __name__ ==  '__main__':
    # 创 建一个对象
    client = Fdfs_client('client.conf')
    #上传文件
    ret = client.upload_by_filename('/home/python/Desktop/1.jpg')
    print(ret)
