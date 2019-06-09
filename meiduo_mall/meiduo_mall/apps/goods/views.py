from django.shortcuts import render
from django.views.generic import View
from .models import GoodsCategory
from meiduo_mall.utils.category import get_category
#分页
from django.core.paginator import Paginator
# Create your views here.
class ListView(View):
    def get(self, request, category_id, page_num):
        # 查询当前指定分类对象
        try:
            category3 = GoodsCategory.objects.get(pk=category_id)
        except:
            return render(request, '404.html')
        categories=get_category()
        category2=category3.parent
        category1=category2.parent
        breadcrumb={
            'cat1':{
                'name':category1.name,
                'url':category1.goodchannel_set.all()[0].url
            },
            'cat2':category2,
            'cat3':category3
        }
        skus=category3.sku_set.filter(is_launched=True)
        sort =request.GET('sort','default')
        #价格
        if sort =='price':
            skus=skus.order_by('price')
        #人气
        elif sort=='hot':
            skus=skus.order_by('-sales')
        #默认
        else:
            skus=skus.order_by('-id')
        #一页有几条数据
        paginator=Paginator.page(skus,5)
        #第几条数据
        page_skus=paginator.page(page_num)
        context={'categories':categories,
                 'breadcrumb':breadcrumb,
                 'sort':sort,
                 'page_skus':page_skus,
                 'category':category3

                 }

        return render(request, 'list.html',context)
