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
from tan_app import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    


    path("",views.home,name="home"),
    path("register",views.register,name="register"),
    path("login",views.login,name="login"),
    path("logout",views.logout  ,name="logout"),
    path("userSessionC",views.userSessionCheck  ,name="userSessionCheck"),
    path("saveQuotation",views.saveQuotation,name="saveQuotation"),

    path("payment",views.payment,name="payment"),
    path("paymenthandler",views.paymenthandler),
    path("gSP",views.governmentServicesPayment,name="governmentServicesPayment"),
    path("governmentServicesPaymentHandler",views.governmentServicesPaymentHandler),
    path("buisnessL",views.buisnessLicence,name="buisnessLicence"),
    path('trav',views.travel,name="travel"),
    
    path("sendOt",views.sendOtp,name="sendOtp"),
    path('verifyOt',views.verifyOtp,name="verifyOtp"),
    path('changePass',views.changePassword,name="changePassword"),

    path("status",views.status),
    path('saveImage',views.saveImage),
    path("category",views.sub_category),
    path("sub_category",views.subSubCat),
    path("blog",views.blog,name="blog"),

    # new
    path("blog/<str:id>",views.blog,name="blog"),

    path("about",views.about),
    path("contact",views.contact)

]

