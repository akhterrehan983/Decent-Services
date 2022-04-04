"""tanweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tan_admin import views
# from tan_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adminpanel/', views.home,name="admin_home"),
    path('objlist', views.objlist,name="objlist"),
    path('delete',views.delete,name="delete"),
    path('add_category',views.add_category,name="add_category"),
    path('adminpanel/admin_login',views.admin_login,name="admin_login"),
    path('adminpanel/admin_logout',views.admin_logout,name="admin_logout"),
    path('edit',views.edit,name="edit"),
    path('edit_category',views.edit_category,name="edit_category"),

    path('writeBlog',views.writeBlog,name="writeBlog"),
    path('readBlog',views.readBlog,name="readBlog"),
    path('deleteBlog',views.deleteBlog,name="deleteBlog"),

    path('delUser',views.delUser,name="delUser"),
    path('getQ',views.getQuotation,name="getQuotation"),
    path('getP',views.getPayment,name="getPayment"),
    path('delQ',views.delQuotation,name="delQuotation"),
    path('delP',views.delPayment,name="delPayment"),
    path('checkBQ',views.checkboxQuotation,name="checkboxQuotation"),
    path('checkBP',views.checkboxPayment,name="checkBoxPayment"),
    
    

    # path('app_home',views.app_home,name="app_home"),
   
]

