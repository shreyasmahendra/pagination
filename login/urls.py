from django.contrib import admin
from django.urls import path
from .import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/',views.register, name="register"),
    path('login/',views.login, name="login"),
    path('home/',views.helo, name="home"),
    path('register/add/',views.add),
    path('login/authenticate/',views.authenticate),
    path('pagination_limit/',views.authenticate1),
    path('pagination/',views.listing),
    path('pagination1/',views.PaginationHelper.as_view()),
    path('users1/', views.users),
    path('users/?limit=10',views.pagination),
    path('users/',views.users_list),
    path('users_end/',views.ending_list),
    path('userspagination/limit/' , views.cursor),
    path('userapi/',views.userlist.as_view()),
    path('TestLinkHeaderPagination/',views.TestLinkHeaderPagination.as_view()),
    path('header/',views.headers),
]