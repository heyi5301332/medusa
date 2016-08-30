#!/usr/bin/env python
# coding:utf-8

import os
import datetime
import random
import json

from django.conf import settings
from django.http import HttpResponse
from django.template import Template,Context
from django.template.loader import get_template
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files import File
from django.core.files.images import ImageFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from myapp.models import News

import requests


class DownloadView(View):
    """
    文件下载功能测试
    """
    # # [1] 文件流(string)
    # def get(self, request, *args, **kwargs):
    #     # os.getcwd() = '/home/workspace/medusa/medusaserver'
    #     file_download = 'README.md'
    #     with open(file_download) as f:
    #         content = f.read()
    #     response = HttpResponse(content)
    #     response['Content-Type'] = 'application/octet-stream'
    #     response['Content-Disposition'] = 'attachment;filename="%s"' % file_download
    #     return response

    # # [2] 迭代器(iterator)
    # def get(self, request, *args, **kwargs):
    #     # an iterator that yields strings as content
    #     def file_iterator(file_name, size_byte=64):
    #         with open(file_name) as f:
    #             while True:
    #                 content = f.read(size_byte)
    #                 if content:
    #                     yield content
    #                 else:
    #                     break
    #     # os.getcwd() = '/home/workspace/medusa/medusaserver'
    #     file_download = 'README.md'
    #     response = HttpResponse(file_iterator(file_download))
    #     response['Content-Type'] = 'application/octet-stream'
    #     response['Content-Disposition'] = 'attachment;filename="%s"' % file_download
    #     return response

    # [3] 下载代理(利用requests实现)
    def get(self, request, *args, **kwargs):
        # url = 'http://records.cloud.chivox.com/57a004e72bedada5b80109f3.mp3'
        # url = 'http://photos.breadtrip.com/photo_2016_06_25_b696dd78fbb4be3c42a2bb421296bc9e.jpg'
        url = request.GET.get('url')
        basename = os.path.basename(url)
        resp = requests.get(url)
        response = HttpResponse(content=resp.content)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % basename
        return response


class TestTemplateView(View):
    """
    渲染模板
    """
    def get(self, request, *args, **kwargs):
        context = {}
        context.update(none_value=None)
        template = 'test.html'
        return render_to_response(template, context)


class TreeView(View):
    """
    echarts 显示树状结构
    """
    def get(self, request, *args, **kwargs):
        context = {}
        a, b, c, d, e, f, g = 'A', 'B', 'C', 'D', 'E', 'F', 'G'
        tree = {
            a: [b, c],
            b: [d, e],
            c: [],
            d: [f, g],
            e: [],
            f: [],
            g: [],
        }
        context.update(tree=tree)
        template = 'tree.html'
        return render_to_response(template, context)




class NewsListView(View):
    """
    新闻列表
    """
    def get(self, request, *args, **kwargs):
        # 关键字参数和分页参数
        keyword = request.GET.get('keyword')
        page = request.GET.get('page', 1)
        # 查询数据库
        news = News.objects.order_by('-datetime_updated')
        # 过滤掉没有图片的新闻条目
        news = news.filter(img__isnull=False)
        if keyword:
            strict = Q(title__icontains=keyword) | \
                     Q(desc__icontains=keyword)
            news = news.filter(strict)
            pass
        # 分页
        paginator = Paginator(object_list=news, per_page=10)
        try:
            pager = paginator.page(page)
        except PageNotAnInteger:
            pager = paginator.page(1)
        except EmptyPage:
            pager = paginator.page(paginator.num_pages)
            pass
        # 分页片段中使用 pager.queries 达到在翻页时带着查询参数的目的
        pager.queries = "keyword=%s" % (keyword or '',)
        # [网页模板]和[通用分页片段(pagination_jinja.html)]中使用 "page" 来访问 Page object
        context = dict()
        context['keyword'] = keyword
        context['page'] = pager
        return render_to_response('news_list.html', context)


class ExceptionTestView(View):
    """
    测试 Sentry 监控异常
    """
    def get(self, request, *args, **kwargs):
        try:
            1/0
        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
        return HttpResponse()
