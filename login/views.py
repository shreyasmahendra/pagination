import io

import form as form
from django.shortcuts import render
from django.http import HttpResponse
import json
from django.http import HttpResponseRedirect
from django.db import connection
from requests import session
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from sqlalchemy.dialects.mysql import pymysql
from django.contrib.auth import authenticate
from .models import User
from django.urls import reverse
from django.core.paginator import Paginator
import stripe
from django.views import View
from .serializers import UserSerializer
from rest_framework.generics import ListAPIView
from .mypaginations import MyLimitOffsetPagination


import pytest
from rest_framework import exceptions
from rest_framework.pagination import PAGE_BREAK, PageLink
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

import drf_link_header_pagination
factory = APIRequestFactory()

# Create your views here.

def users_list(request):
    charlist = []
    for user in User.objects.all().order_by('id')[:10]:
        charlist.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
        })
    response = {"next_url": [], "previous_url": [], "body": []}
    response["next_url"] = 'http://127.0.0.1:8000/users_end/?limit=10'
    response["previous_url"] = 'http://127.0.0.1:8000/users/?limit=10'
    response["body"] = charlist
    return HttpResponse(json.dumps(response), content_type="application/json")

def ending_list(request):
    charlist = []
    for user in User.objects.all().order_by('id')[10:20]:
        charlist.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
        })
    response = {"next_url": [], "previous_url": [], "body": []}
    response["next_url"] = 'http://127.0.0.1:8000/users_end/?limit=10'
    response["previous_url"] = 'http://127.0.0.1:8000/users/?limit=10'
    response["body"] = charlist
    return HttpResponse(json.dumps(response), content_type="application/json")

def listing(request):
    items = User.objects.raw('SELECT * FROM `login_user`WHERE id LIMIT 10 OFFSET 0')
    print(items[1])
    paginator = Paginator(items, 10) # Show 10 contacts per page.
    page_number = request.GET.get('limit')
    page_obj = paginator.get_page(page_number)
    response = {"next_url": [],"previous_url": [],"body": {}}
    # b = []
    # for a in page_obj:
    #     pass
    #     print(a)
    #
    #     items.append({
    #         'id': a.id,
    #         'name': a.name,
    #         'email': a.email,
    #         'password': a.password,
    #     })
    response["next_url"]=  'http://127.0.0.1:8000/pagination/'
    response["previous_url"]=  'http://127.0.0.1:8000/pagination/'
    type(page_obj)
    response["body"]= page_obj
    return HttpResponse(json.dumps(response), content_type="application/json")

    #return render(json.dumps(page_obj),content_type="application/json")
    #return render(request,'login/edit.html',{'page_obj': page_obj})

def users(request):
    items = []
    for users in User.objects.all():
        items.append({
            'id': users.id,
            'name': users.name,
            'email': users.email,
            'password': users.password,
        })
    return HttpResponse(json.dumps(items),content_type="application/json")

def pagination(request):
    print("pagination")
    items = User.objects.raw('SELECT * FROM `login_user` WHERE id LIMIT 10 OFFSET 0')
    print(len(items))
    p = Paginator(items,4)
    print(p.num_pages)
    page_number = request.GET.get('limit')
    page_obj = p.get_page(page_number)
    # b = []
    # for a in page_obj:
    #     items.append({
    #         'id': a.id,
    #         'name': a.name,
    #         'email': a.email,
    #         'password': a.password,
    #     })
    return HttpResponse(json.dumps(page_obj),content_type="application/json")



class PaginationHelper(View):
    charlist=[]
    for users in User.objects.all().order_by('id')[:10]:
        charlist.append({
            'id': users.id,
            'name': users.name,
            'email': users.email,
        })
    response = {"next_url": [], "previous_url": [], "body": []}
    response["next_url"] = 'http://127.0.0.1:8000/users/'
    response["previous_url"] = 'http://127.0.0.1:8000/users/'
    response["body"] = charlist


    def __init__(self,users):
        self.items = users
        self.items_per_page = 100

    def items_count(self):
        return len(self.items)
    def page_count(self):
        if self.items_count()%self.items_per_page == 0:
            return self.items_count()/self.items_per_page
        else:
            return self.items_count()//self.items_per_page + 1
    def page_item_count(self,page_index):
         if page_index >= self.page_count():
             return -1
         elif page_index == self.page_count() -1:
             return self.items_count() - self.items_per_page*page_index
         else:
             return self.items_per_page
    def page_index(self,item_index):
        if item_index in range(self.items_count()):
            return item_index//self.items_per_page
        else:
            return -1

def register(request):
    context ={

    }
    return render(request,"login/register.html",context)

def add(request):
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)
    if request.content_type == 'application/json':
        body = request.body
        body = body.decode('utf-8')
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return HttpResponse("invalid detail", status=400)
        if 'name' not in body:
            return HttpResponse("please enter the name", status=400)
        if 'email' not in body:
            return HttpResponse("please enter the email", status=400)
        if 'password' not in body:
            return HttpResponse("please enter the password", status=400)
        name = body['name']
        email = body['email']
        password = body['password']
    else:

        if 'name' not in request.POST:
            return HttpResponse("please enter name", status=400)
        if 'email' not in request.POST:
            return HttpResponse("please enter email", status=400)
        if 'password' not in request.POST:
            return HttpResponse("please enter password", status=400)
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

    if User.objects.filter(email=email).exists():
        return HttpResponse(email + " already exist", status=409)
    User(name=name, email=email, password=password).save()
    return HttpResponseRedirect(reverse('home'))


def login(request):
    context={

    }
    return render(request , 'login/index.html', context)

def authenticate1(request):
    with connection.cursor() as cursor:

        cursor.execute('SELECT * FROM `login_user`WHERE id LIMIT 10 OFFSET 0')

        row = cursor.fetchall()
        return HttpResponse(json.dumps(row),content_type="application/json")

def authenticate(request):
    name = request.POST['name']
    password = request.POST['password']
    User = authenticate(name=name, password=password)


    # Prepare database connection
    # name = request.get('name')
    # password = request.get('password')

    with connection.cursor() as cursor:
        # Execute the vulnerable SQL query concatenating user-provided input.
        cursor.execute("SELECT * FROM login_user WHERE name = '%s' AND password = '%s'" % (name, password))

    # If the query returns any matching record, consider the current user logged in.
        record = cursor.fetchone()
        return record
    # disconnect from server


    # with connection.cursor() as cursor:
    #     cursor.execute("""
    #            SELECT
    #                name
    #                password
    #            FROM
    #                login_user
    #            WHERE
    #                name = '%s'
    #                password = '%s'
    #        """ % name )
    #     result = cursor.fetchone()
    # return result
    # u = User.objects.filter(name=name, password=password)
    # # if u.exists():
    # query = 'select name from login_user where name = %s ' % name
    # query1 = 'select password from login_user where password = %s ' % password
    # u =User.objects.raw(query + query1)
    # connection.execute("SELECT id,name,email,password FROM login_user WHERE name=%s, password=%s ,LIMIT 1", (name,password))
    # print(u)
    # return HttpResponse("successfully login", status=200)
    # #else:
    #return HttpResponse("invalied details",status=400)
    #return HttpResponseRedirect(reverse('home'))

def helo(request):
    return HttpResponse("welcome to the home page")

def cursor(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM login_user WHERE id > 10 ORDER BY id ASC LIMIT 10')
        row = cursor.fetchall()
        print(type(row))
        if type(row) is list:
            row = dict(row)
    return HttpResponse(json.dumps(row),content_type="application/json")

class userlist(ListAPIView):

    queryset = User.objects.all()
    query = queryset
    print(queryset)
    serializer_class = UserSerializer
    print(serializer_class)
    pagination_class = MyLimitOffsetPagination
    serializer = UserSerializer(User)
    print(serializer.data)
    content = JSONRenderer().render(serializer.data)
    print(content)
    stream = io.BytesIO(content)
    data = JSONParser().parse(stream)
    response = HttpResponse()

    # response = HttpResponse(headers={'next_url':2,'previous_url':10})
    response["next_url"] = "request.headers.next"
    # response["previous_url"] = query
    # def get_object(self,request):
    #     print(self.query)
    #     return response

def headers(self,request):
    json_data = request.body
    print(request.body)
    stream = io.BytesIO(json_data)
    pythondata = JSONParser().parse(stream)
    next_url = pythondata.get('next')
    previous_url = pythondata.get('previous')
    response = HttpResponse()
    response.headers[next_url] ="{" \
                                  "http://127.0.0.1:8000/userapi/?limit=10&offset=10","http://127.0.0.1:8000/userapi/?limit=10&offset=20","http://127.0.0.1:8000/userapi/?limit=10&offset=30","http://127.0.0.1:8000/userapi/?limit=10&offset=40""}".json
    response.headers[previous_url]="{"\
                                     "http://127.0.0.1:8000/userapi/?limit=10","http://127.0.0.1:8000/userapi/?limit=10&offset=10","http://127.0.0.1:8000/userapi/?limit=10&offset=20""}".json

    return response





































class TestLinkHeaderPagination(ListAPIView):
    def setup(self):
        class ExamplePagination(drf_link_header_pagination.LinkHeaderPagination):
            page_size = 5

        self.pagination = ExamplePagination()
        self.queryset = range(1, 101, 10)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_queryset(self.queryset, request))

    def get_paginated_response(self, queryset):
        return self.pagination.get_paginated_response(queryset)

    def get_html_context(self):
        return self.pagination.get_html_context()

    def test_no_page_number(self):
        request = Request(factory.get('/'))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()
        assert queryset == [1, 2, 3, 4, 5]
        assert response.data == [1, 2, 3, 4, 5]
        assert response['Link'] == (
            '<http://testserver/?page=2>; rel="next", '
            '<http://testserver/?page=20>; rel="last"'
        )
        assert context == {
            'previous_url': None,
            'next_url': 'http://testserver/?page=2',
            'page_links': [
                PageLink('http://testserver/', 1, True, False),
                PageLink('http://testserver/?page=2', 2, False, False),
                PageLink('http://testserver/?page=3', 3, False, False),
                PAGE_BREAK,
                PageLink('http://testserver/?page=20', 20, False, False),
            ]
        }
        assert self.pagination.display_page_controls
        assert isinstance(self.pagination.to_html(), type(''))

    def test_second_page(self):
        request = Request(factory.get('/', {'page': 2}))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()
        assert queryset == [6, 7, 8, 9, 10]
        assert response.data == [6, 7, 8, 9, 10]
        assert response['Link'] == (
            '<http://127.0.0.1:8000/>; rel="first", '
            '<http://127.0.0.1:8000/>; rel="prev", '
            '<http://127.0.0.1:8000/userapi/>; rel="next", '
            '<http://127.0.0.1:8000/userapi/>; rel="last"'
        )
        assert context == {
            'previous_url': 'http://127.0.0.1:8000/',
            'next_url': 'http://127.0.0.1:8000/userapi/',
            'page_links': [
                PageLink('http://127.0.0.1:8000/userapi/', 1, False, False),
                PageLink('http://127.0.0.1:8000/userapi/', 2, True, False),
                PageLink('http://127.0.0.1:8000/userapi/', 3, False, False),
                PAGE_BREAK,
                PageLink('http://127.0.0.1:8000/userapi/', 20, False, False),
            ]
        }

    def test_last_page(self):
        request = Request(factory.get('/', {'page': 'last'}))
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        context = self.get_html_context()
        assert queryset == [96, 97, 98, 99, 100]
        assert response.data == [96, 97, 98, 99, 100]
        assert response['Link'] == (
            '<http://127.0.0.1:8000/>; rel="first", '
            '<http://127.0.0.1:8000/?page=19>; rel="prev"'
        )
        assert context == {
            'previous_url': 'http://127.0.0.1:8000/userapi/?limit=10&offset=10',
            'next_url': None,
            'page_links': [
                PageLink('http://127.0.0.1:8000/userapi/', 1, False, False),
                PAGE_BREAK,
                PageLink('http://127.0.0.1:8000/userapi/', 18, False, False),
                PageLink('http://127.0.0.1:8000/userapi/', 19, False, False),
                PageLink('http://127.0.0.1:8000/userapi/', 20, True, False),
            ]
        }