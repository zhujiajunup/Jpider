
import sys
import os
import django
import django.db.models
sys.path.append('../Jpider')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Jpider.settings'
django.setup()

from spiders.models import ShopInfo, ReviewDedail, ShopId

import xlwt


            # 'http://www.dianping.com/search/category/2/10/g110', # 北京火锅
            # 'http://www.dianping.com/search/category/2/10/g107', # 北京台湾菜
            # 'http://www.dianping.com/search/category/2/10/g112', # 北京小吃快餐
            # 'http://www.dianping.com/search/category/2/10/g250', # 北京创意菜
            # 'http://www.dianping.com/search/category/2/10/g116', # 北京西餐
            # 'http://www.dianping.com/search/category/2/10/g113', # 北京日本菜
            # 'http://www.dianping.com/search/category/2/10/g103', # 北京粤菜
            # 'http://www.dianping.com/search/category/2/10/g115', # 北京东南亚菜
            # 'http://www.dianping.com/search/category/2/10/g102', # 北京川菜
            # 'http://www.dianping.com/search/category/1/10/g113', # 上海日本菜？？？
            # 'http://www.dianping.com/search/category/1/10/g110', # 上海火锅
            # 'http://www.dianping.com/search/category/1/10/g107', # 上海台湾菜
            # 'http://www.dianping.com/search/category/1/10/g103', # 上海粤菜
            # 'http://www.dianping.com/search/category/1/10/g102', # 上海川菜
            # 'http://www.dianping.com/search/category/1/10/g112', # 上海小吃快餐
            # 'http://www.dianping.com/search/category/1/10/g115', # 上海东南亚菜
            # 'http://www.dianping.com/search/category/1/10/g116',  # 上海西餐

category_dict = {'g110':'火锅', 'g107':'台湾菜', 'g112':'小吃快餐', 'g250': '创意菜',
                 'g116': '西餐', 'g113': '日本菜', 'g103': '粤菜', 'g115': '东南亚菜', 'g102': '川菜'}

rank_star_dict = {
    '五星商户': 5,
    '准五星商户':4.5,
    '四星商户': 4,
    '准四星商户': 3.5,
    '三星商户': 3,
    '准三星商户': 2.5,
    '二星商户': 2,
    '准二星商户': 1.5,
    '一星商户': 1,
    '准一星商户': 0.5,
    '该商户暂无星级': 0,
    '': '无'
}


workbook = xlwt.Workbook()
sheet = workbook.add_sheet('dazongdianping',cell_overwrite_ok=True)
title = ['餐厅id','城市', '餐厅名称', '餐厅地点', '餐厅地址', '餐厅类别', '人均价格', '是否参加营销活动', '营业时间', '点评数量',
         '总体评分', '口味评分', '环境评分', '服务评分', '五星', '四星', '三星', '二星', '一星', '第一条评论时间']
for i in range(len(title)):
    sheet.write(0, i, title[i] )

shops = ShopInfo.objects.all()


for j in range(1, len(shops)+1):
    shop = shops[j-1]
    info_list = []
    info_list.append(shop.shop_id) # id
    print(shop.shop_id)
    try:
        url = ShopId.objects.get(pk=shop.shop_id).from_url
    except ShopId.DoesNotExist:
        continue
    if url is None:
        continue
    city_no = url.split('/')[-3]
    city = '北京' if city_no == '2' else '上海'
    info_list.append(city)
    category = category_dict[url.split('/')[-1][:4]]
    info_list.append(shop.shop_name)
    info_list.append(shop.place if shop.place is not None else '')
    info_list.append(shop.address if shop.address is not None else '')
    info_list.append(category)
    avg_price = shop.avg_price.split('：')[1]
    if len(avg_price) != 1:
        avg_price = avg_price[:-1]

    info_list.append(avg_price )

    info_list.append(shop.feature2)
    info_list.append(shop.open_time.replace('\t', ' ').replace('\n', ';') if shop.open_time is not None else '')
    info_list.append(shop.review_count[:-3])
    info_list.append(rank_star_dict[shop.rank_star])
    info_list.append(shop.taste.split('：')[1])
    info_list.append(shop.env.split('：')[1])
    info_list.append(shop.service.split('：')[1])

    review = ReviewDedail.objects.get(pk=shop.shop_id)
    info_list.append(review.star_5)
    info_list.append(review.star_4)
    info_list.append(review.star_3)
    info_list.append(review.star_2)
    info_list.append(review.star_1)
    info_list.append(review.first_review_time)
    for i in range(len(info_list)):
        if info_list[i] is None:
            info_list[i] = ' '
    # 'http://www.dianping.com/search/category/2/10/g110', # 北京火锅
    # 'http://www.dianping.com/search/category/2/10/g107', # 北京台湾菜
    # 'http://www.dianping.com/search/category/2/10/g112', # 北京小吃快餐
    # 'http://www.dianping.com/search/category/2/10/g250', # 北京创意菜
    # 'http://www.dianping.com/search/category/2/10/g116', # 北京西餐
    # 'http://www.dianping.com/search/category/2/10/g113', # 北京日本菜
    # 'http://www.dianping.com/search/category/2/10/g103', # 北京粤菜
    # 'http://www.dianping.com/search/category/2/10/g115', # 北京东南亚菜
    # 'http://www.dianping.com/search/category/2/10/g102', # 北京川菜
    # 'http://www.dianping.com/search/category/1/10/g113', # 上海日本菜？？？
    # 'http://www.dianping.com/search/category/1/10/g110', # 上海火锅
    # 'http://www.dianping.com/search/category/1/10/g107', # 上海台湾菜
    # 'http://www.dianping.com/search/category/1/10/g103', # 上海粤菜
    # 'http://www.dianping.com/search/category/1/10/g102', # 上海川菜
    # 'http://www.dianping.com/search/category/1/10/g112', # 上海小吃快餐
    # 'http://www.dianping.com/search/category/1/10/g115', # 上海东南亚菜
    # 'http://www.dianping.com/search/category/1/10/g116',  # 上海西餐
    # file = open('/Users/didi/crawler/output/%s_%s.txt' % (city, category), 'a')
    # file.write('\t'.join(info_list)+'\n')
    # file.close()
    print(info_list)
    info_list.clear()