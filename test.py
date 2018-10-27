
import requests
import re
from urllib.parse import (urlencode, urlsplit)
import json

def test_zz():
    urls = ['https://cn.maxmara.com/coats/c-101',
           'https://cn.maxmara.com/abiti-sposa',
           'https://cn.maxmara.com/101801-iconic-coat']
    
    for url in urls:
        #get the script, and write to file
        cata = url.split('/')[-1]
        print(cata)
        file = '{}.html'.format(cata)
        # res = requests.get(url)
        # with open(file, 'w') as f:
        #     f.write(res.text)


        content = None
        with open(file, 'r') as f:
            content = f.read()
        
        #if normal one
        patten = re.compile(r'/c-\d+?$',re.I|re.M|re.S)
        print(patten)
        searchObj = patten.search(url)
        print(searchObj)
        patten = None
        if searchObj:
            print(searchObj.group())
            patten = re.compile(r'<li class="span3 item_thumb product-card" data-product-id="(.+?)".*?<a href="(.+?)".*?</li>', re.I|re.M|re.S)
            products = patten.findall(content)
            # searchObj = re.findall(patten, content)
            for product in products:
                print(product)
            print(len(products))
        else:
            is_product_gallery = re.search(r'isProductGallery = true', content, re.M|re.I)
            if is_product_gallery:
                patten = re.compile(r'<li class="span3 item_thumb">\s+?<div id="product-code-(\d+?)".*?<a href="(.+?)".+?</li>', re.I|re.M|re.S)
                # products = patten.findall(content)
                print(patten)
                # searchObj = patten.search(content)
                # print(searchObj)
                # if searchObj:
                #     print(searchObj.group())
                products = patten.findall(content)
                for product in products:
                    print(product)
                print(len(products))
            else:
                patten = re.compile(r'<a href="(/p-.+?)".+?a>', re.I|re.M|re.S)
                print(patten)
                products = patten.findall(content)
                for product in products:
                    print(product)
                print(len(products))
        
def test_ajax():
    url = 'https://cn.maxmara.com/coats/c-101/resultsViaAjax?'
    post_data =dict(
        q=':topRated:collectionActive:true',
        sort='topRated',
        numberOfPage=0,
        # categoryCode=202,
        numberOfClothes=16,
        numberOfClothesPE=16,
        scrollTop='')
    url = url + urlencode(post_data)
    res = requests.get(url)
    # print(res.text)
    d = json.loads(res.text)
    with open('w_ajax.json', 'w') as f:
        json.dump(d, f, indent=2)
    total_page = json.loads(res.text)['totalPage']
    print(total_page)
    product_list = d['searchPageData']['results'][0]['productList']
    for product in product_list:
        product_keys = ("code","name","url")
        item ={}
        for key in product_keys:
            item[key] = product[key]
        print(item)


def zz2():
    url = 'https://cn.maxmara.com/coats/c-101/resultsViaAjax?q=%3AtopRated%3AcollectionActive%3Atrue%3AfilterEnabled%3Atrue&sort=topRated&numberOfPage=2&categoryCode=101&numberOfClothes=16&numberOfClothesPE=16&scrollTop=&_=1540029796456'
    patten = re.compile('numberOfPage=(\d+?)&')
    searchObj = patten.search(url)
    if searchObj:
        print(searchObj.group())
    # url2 = patten.sub(url,'numberOfPage=199&')
    current_page = searchObj.group(1)
    print(current_page)
    next_page = int(current_page) + 1
    url2 = re.sub(patten, 'numberOfPage={}&'.format(next_page), url)
    print(url2)

                

def test_dir():
    import sys
    import os
    from os.path import dirname
    path = dirname(dirname(os.path.abspath(os.path.dirname(__file__))))
    # print(__file__)
    print(os.path.abspath(__file__))
    print(os.path.dirname(os.path.abspath(__file__)))
    print(dirname(os.path.dirname(os.path.abspath(__file__))))
    print(path)
    sys.path.append(path)        


if __name__ == "__main__":
    test_dir()