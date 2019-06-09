from django.shortcuts import render
from django.views import View
from goods.models import GoodsCategory, GoodsChannel
from meiduo_mall.utils import category
from .models import Contentcategory, Content


class IndexView(View):
    def get(self, request):
        categories = category.get_category()
        #广告分类的所有的查询集
        contents = Contentcategory.objects.all()
        content_dict = {}
        for content in contents:
            #一类广告的所有的广告信息
            content_dict[content.key] = content.content_set.filter(status=True).order_by('sequence')
        context = {
            'categories': categories,
            'contents':content_dict,
        }

        return render(request, 'index.html', context)
