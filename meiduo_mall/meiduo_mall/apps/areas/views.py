from django.shortcuts import render
from django import http
from meiduo_mall.utils.response_code import RETCODE
from django.views.generic import View
from areas.models import Area
# 缓冲
from django.core.cache import cache


class AreaView(View):
    def get(self, request):
        area_id = request.GET.get('area_id')
        if area_id is None:
            province_List = cache.get('province_List')
            if province_List is None:
                paves = Area.objects.filter(parent__isnull=True)
                province_List = []
                for pave in paves:
                    province_List.append({
                        'id': pave.id,
                        'name': pave.name,
                    })
                province_List = cache.set('province_List', province_List, 3600)
            return http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': 'ok',
                'province_list': province_List
            })
        else:
            sub_data = cache.get('area_id' + area_id)
            if sub_data is None:
                try:

                    area = Area.objects.get(pk=area_id)
                except:
                    return http.JsonResponse({
                        'code': RETCODE.PARAMERR,
                        'errmsg': '信息无效',
                    })
                else:
                    subs = area.subs.all()
                    sub_list = []
                    for sub in subs:
                        sub_list.append({
                            'id': sub.id,
                            'name': sub.name,
                        })
                    sub_data = {
                        'id': area.id,
                        'name': area.name,
                        'subs': sub_list
                    }
                    cache.set('area_' + area_id, sub_data, 3600)
            return http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': 'ok',
                'sub_data': sub_data
            })
