from meiduo_mall.apps.goods.models import GoodsChannel

def get_category():
    # 频道分类信息
    # 查询频道
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    categories = {}
    # 遍历频道，获取 一级分类二级分类
    for channel in channels:
        if channel.group_id not in categories:
            # 如果不存在则创建新字典
            categories[channel.group_id] = {
                'channels': [],  # 一级分类
                'sub_cats': []  # 二级分类
            }
        channel_dict = categories[channel.group_id]
        channel_dict['channels'].append({
            'name': channel.category.name,  # 一级分类的名称
            'url': channel.url  # 频道的链接
        })
        # 向频道中添加二级分类
        catetory2s = channel.category.subs.all()
        # 6.遍历频道中逐个添加二级分类
        for catetory2 in catetory2s:
            channel_dict['sub_cats'].append({
                'name': catetory2.name,  # 二级分类名称
                'sub_cats': catetory2.subs.all()  # 三级分类
            })
    return categories