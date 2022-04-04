from django.core.files import storage
from django.core.files.storage import FileSystemStorage,default_storage
from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from pyasn1.type.univ import ObjectIdentifier
from pyasn1_modules.rfc2459 import Dss_Parms 
import pyrebase
from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django.core.mail import send_mail

# importing module
import logging
 # Create and configure logger
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 # Creating an object
global logger
logger = logging.getLogger()
 # Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)
print(logger)
firebaseConfig = {
"apiKey": "AIzaSyCECvSBvG4F4WSuwuz3_1VTj594sMmWbLI",
"authDomain": "tanweb-77381.firebaseapp.com",
"databaseURL": "https://tanweb-77381-default-rtdb.firebaseio.com",
"projectId": "tanweb-77381",
"storageBucket": "tanweb-77381.appspot.com",
"messagingSenderId": "739284794169",
"appId": "1:739284794169:web:f97b9ff52574359e8f46e8",
"measurementId": "G-NMNJHRDC5H"
};
#   Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
database = firebase.database()
storage = firebase.storage()


@csrf_exempt
def getPayment(request):
    if request.is_ajax():
        choosenType = request.POST.get('chooseType')
        payment = []
        for i in database.child(choosenType).get().each():
            if type(i.val())!= int:
                payment.append(i.val())
        z = "{} Payment".format(choosenType)
        logger.info(z)
        print(z)
        return JsonResponse({"payment":payment[::-1]})
    
def getQuotation(request):
    if request.is_ajax():
        choosenType = request.GET.get('chooseType')
        print(choosenType)
        quotation=[]
        
        if choosenType == "Vehicle Insurance":
            for i in database.child("quotation").get().each():
                if type(i.val())==dict and i.val()["serviceType"]==choosenType:
                    quotation.append(i.val())
                print(type(i.val()))
            print(quotation)
            return JsonResponse({"quotation":quotation,"status": "successgetQVH"})

        elif choosenType in ["Health Insurance","Term Insurance"]:
            for i in database.child("quotation").get().each():
                if type(i.val())!= int and len(i.val())==3 and i.val()[2]["serviceType"]==choosenType:
                    quotation.append(i.val())
            return JsonResponse({"quotation":quotation,"status": "successsuccessget HV or TH"})
        
        elif choosenType == "Buisness Licence":
            for i in database.child("buisnessLicence").get().each():
                if i.key()!="id":
                    quotation.append(i.val())
            print(quotation)
            return JsonResponse({"quotation":quotation,"status": "successgetBuisnessLicense"})
        else:
            return JsonResponse({"status": "successgetQuotation"})
      
    else:
            return JsonResponse({"status": "getQ"})

def delQuotation(request):
    if request.is_ajax():
        idd = int(request.GET.get("id"))
        serviceType = request.GET.get('serviceType')
        print(type(idd))
        print(idd)
        print(serviceType)
        if  serviceType == "Vehicle Insurance":
            for i in database.child("quotation").get().each():
                if type(i.val())==dict and serviceType == i.val()["serviceType"] and i.val()["id"]==idd:
                    database.child("quotation").child(i.key()).remove()
                    # print("delVh")
                    return JsonResponse({"info":serviceType})
            else:
                return JsonResponse({"status":"failure"})
        elif serviceType in ["Health Insurance","Term Insurance"]:
            for i in database.child("quotation").get().each():
                if type(i.val())==list and serviceType == i.val()[2]["serviceType"] and i.val()[2]["id"] == idd :
                    database.child("quotation").child(i.key()).remove()
                    # print("del"+"heatlh")
                    return JsonResponse({"info":serviceType})
            else:
                return JsonResponse({"status":"failure"})
    else:
        return JsonResponse({"status":"not found"})

def delPayment(request):
    if request.is_ajax():
        idd = int(request.GET.get("id"))
        name = request.GET.get("name")
        print(idd,name)
        for i in database.child(name).get().each():
            if type(i.val())!=int and i.val()["id"] == idd:
                database.child(name).child(i.key()).remove()
        return JsonResponse({"info":"Success"})
def checkboxPayment(request):
    if request.is_ajax():
        idd = int(request.GET.get("id"))
        checkbox = request.GET.get("checkbox")
        type = request.GET.get("type")
        
       

        for i in database.child(type).get().each():
            if i.key()!="vi_id" and idd == i.val()["id"]:
                database.child(type).child(i.key()).update({ checkbox:not(i.val()[checkbox]) }) 
                email = request.GET.get("email")
                name = request.GET.get("name")
                serviceType = request.GET.get("serviceType")
                if email!="":
                    subject = f'Dear {name}'
                    if checkbox=="readUnread":
                        message = f'Thank you for contacting us, your service request for {serviceType} is in process.'
                    elif checkbox == "status":
                        message = f'Thank you for contacting us, your service request for {serviceType} has been completed.'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [email]
                    send_mail( subject, message, email_from, recipient_list )
                print(email,"success")
                return JsonResponse({"info  ":"success"})
        return JsonResponse({"info":"failure"})
    else:
        return JsonResponse({"info":"BAD REQUEST"})
    
        

def checkboxQuotation(request):
    if request.is_ajax():
        idd = int(request.GET.get("id"))
        serviceType = request.GET.get("serviceType")
        checkbox = request.GET.get("checkbox")
        print(serviceType,checkbox,idd)
        if serviceType == "Vehicle Insurance":
            for i in database.child("quotation").get().each():
                if type(i.val())==dict and serviceType == i.val()["serviceType"] and i.val()["id"]==idd:
                    database.child("quotation").child(i.key()).update({checkbox:not(i.val()[checkbox])})
                    email = i.val()["user"]["email"]
                    name = i.val()["user"]["name"]
                    if email!="":
                        subject = f'Dear {name}'
                        if checkbox=="readUnread":
                            message = f'Thank you for contacting us, your service request for {serviceType} is in process.'
                        elif checkbox == "status":
                            message = f'Thank you for contacting us, your service request for {serviceType} has been completed.'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [email]
                        send_mail( subject, message, email_from, recipient_list )
                    return JsonResponse({"info":"SuccessVechicleInsuranceQuotation"})
            else:
                return JsonResponse({"info":"FailedVechicleInsuranceQuotation"})

        elif serviceType in ["Health Insurance","Term Insurance"]:
            for i in database.child("quotation").get().each():
                if type(i.val())==list and serviceType == i.val()[2]["serviceType"] and i.val()[2]["id"] == idd :
                    database.child("quotation").child(i.key()).child(2).update({checkbox:not(i.val()[2][checkbox])})
                    email = i.val()[0]["user"]["email"]
                    name = i.val()[0]["user"]["name"]
                    if email!="":
                        subject = f'Dear {name}'
                        if checkbox=="readUnread":
                            message = f'Thank you for contacting us, your service request for {serviceType} is in process.'
                        elif checkbox == "status":
                            message = f'Thank you for contacting us, your service request for {serviceType} has been completed.'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [email]
                        send_mail( subject, message, email_from, recipient_list )
                    return JsonResponse({"info":"HI or VI checkBox success"})
            else:
                return JsonResponse({"info":"HI or VI checkBox success"})

    else:
        return JsonResponse({"status":"not found"})

def delUser(request):
    idd = int(request.GET.get('id'))
    for i in database.child("user").get().each():
        if i.val()["id"] == idd:
            database.child("user").child(i.key()).remove()
            return JsonResponse({"info":"deleteSuccess"})
    return JsonResponse({"info":"deleteFailure"})
            

@csrf_exempt
def writeBlog(request):
    if request.is_ajax():
        category = request.POST.get("category")
        content = request.POST.get("content")
        heading = request.POST.get("heading")
        blogId = database.child("blog").child("blog_id").get().val()+1
        database.child("blog").update({"blog_id":blogId})
        print(category+content+heading)
        category_id = -1
        for i in database.child("sub_category").get().each():
            if i.val()["heading"]  == category:
                category_id = i.val()["sub_cat_id"]
                break
        for i in database.child("main_category").get().each():
            if i.val()["heading"]  == category:
                category_id = i.val()["cat_id"]
                break

        data = {"blogId":blogId,"content":content,"categoryId":category_id,"heading":heading}
        database.child("blog").push(data)
        return JsonResponse({"status":"writeblogsuccess"})
    else:    
        return JsonResponse({"status":"writeblogfailure"})

def readBlog(request):
    l=[]
    for i in database.child("blog").get().each():
        if type(i.val())!=int:
            l.append(i.val())
    return JsonResponse({'l':l})

def deleteBlog(request):
    blogId = request.GET.get('blogId')
    for i in database.child("blog").get().each():
        if i.val()["blogId"] == int(blogId):
            database.child("blog").child(i.key()).remove()
            return JsonResponse({"info":"success"})
    
    return JsonResponse({"info":"failure"})





def home(request):
   
    if "email" in request.session:
        l=[]
        for i in database.get().each():
            if i.key() in ["blog","user","quotation"]:
                l.append(i.key())
                print(i.key())
        
        l.append("Payment")
        return render(request,"admin_home.html",context={'l':l})
        # return render(request,"tan_app_temp/header.html")

    else:
        return render(request,"admin_login.html")

def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if email=="tan@gmail.com" and password=="tan":
            request.session["email"]=email
            return home(request)
        else:
            messages.success(request,"wrong email or password")
            return render(request,"admin_login.html")
            # return redirect("")
            # return HttpResponse('')
        
    else:
        return render(request,"admin_login.html")




def admin_logout(request):
    if "email" in request.session:
        del request.session["email"]
    return render(request,"admin_login.html")


def objlist(request,info=None):
    if info is None:
        info = request.GET.get('data')
    print(info)
    # print(info)
    if info == "Payment":
        payment = []
        for i in database.child("governmentServices").get().each():
            if type(i.val())!=int:
                payment.append(i.val())
        return render(request, 'tan_admin/payment.html',context={"payment":payment})
    if info != "blog":
        data = database.child(info).get()
        l=[]
        for i in data:
            # print(i.val())
            l.append(i.val())
    data=[]
    if info == "sub_category":
        for i in database.child('main_category').get().each():
            # print(i.val()["heading"])
            data.append(i.val()["heading"])
    
    elif info == "sub_sub_category":
        for i in database.child('sub_category').get().each():
            # print(i.val()["heading"])
            data.append(i.val()["heading"])
    
    elif info == "blog":
        for i in database.child('sub_category').get().each():
            data.append(i.val()["heading"])

        for i in database.child('main_category').get().each():
            data.append(i.val()["heading"])
        
        return render(request,"admin_blog.html",context={"data":data})
        # return render(request,"writeBlog.html",context={"data":data})


    elif info == "user":
        user=[]
        for i in database.child("user").get().each():
            if i.key()!="user_id":
                user.append(i.val())
        return render(request,"user.html",context={"user":user})

    elif info == "quotation":
        quotation=[]
        for i in database.child("quotation").get().each():
            if i.key()!="id" and "serviceType" in i.val():
                quotation.append(i.val())
        return render(request,"insurance_quotation.html",context={"quotation":quotation})
    # print(l)
    return render(request,"objlist.html", context={'info':info,'data':data,'l':l})

def delete(request):
    # print(request.GET.get('cat_id'))
    # print(request.GET.get('sub_cat_id'))
    cat_id = request.GET.get('cat_id')
    sub_cat_id = request.GET.get('sub_cat_id')
    sub_sub_cat_id = request.GET.get('sub_sub_cat_id')
    print(sub_sub_cat_id)
    if cat_id!=None:
        # return HttpResponse('catid')
        print("cat_id=",cat_id)
        for i in database.child("main_category").get().each():
            print(i.key())
            print(str(i.val()["cat_id"]),cat_id)
            if str(i.val()["cat_id"]) == cat_id:
                database.child("main_category").child(i.key()).remove()
                return objlist(request,"main_category")
                break
                
    elif sub_cat_id!=None:
        # return HttpResponse('subcatid')
        for i in database.child("sub_category").get().each():
            if str(i.val()["sub_cat_id"]) == sub_cat_id:
                database.child("sub_category").child(i.key()).remove()
                return objlist(request,"sub_category")
                break
    
    elif sub_sub_cat_id!=None:
        # return HttpResponse('subcatid')
        for i in database.child("sub_sub_category").get().each():
            if str(i.val()["sub_sub_cat_id"]) == sub_sub_cat_id:
                database.child("sub_sub_category").child(i.key()).remove()
                return objlist(request,"sub_sub_category")
                break
    return HttpResponse('delete')



def edit(request):
    # print("request")
    if request.is_ajax():
        # print(request.GET.get('type'))
        # print(request.GET.get('id'))
        _type = request.GET.get('type')
        id = request.GET.get('id')
        # print(_type,id)
        if _type == "edit_main":
            for i in database.child("main_category").get().each():
                
                if str(i.val()["cat_id"]) == id:
                    # print(i.val())
                    return JsonResponse({"edit":"edit","data":i.val()})
                    break
            
        elif _type == "edit_sub":
            for i in database.child("sub_category").get().each():
                
                if str(i.val()["sub_cat_id"]) == id:
                    # print(i.val())
                    for j in database.child("main_category").get().each():
                        if str(j.val()["cat_id"]) == str(i.val()["cat_id"]):
                            return JsonResponse({"edit":"edit","data":i.val(),"main_cat_name":i.val()["cat_id"]})
                            break
       
        elif _type == "edit_sub_sub":
            for i in database.child("sub_sub_category").get().each():
                if str(i.val()["sub_sub_cat_id"]) == id:
                    # print(i.val())
                    for j in database.child("sub_category").get().each():
                        if str(j.val()["sub_cat_id"]) == str(i.val()["sub_cat_id"]):
                            return JsonResponse({"edit":"edit","data":i.val(),"main_cat_name":i.val()["sub_cat_id"]})
                            break
        return JsonResponse({"edit":"edit"})





def edit_category(request):
    
    _type = request.POST.get('submit','') 
    heading = request.POST.get('heading','')
    desc = request.POST.get('desc','')
    main_cat = request.POST.get('main_cat',"")
    id = request.POST.get('id','none')
    print(_type,heading,main_cat,id)  
    if _type == "main_category":
        print("main")
        for i in database.child("main_category").get().each():
            # print(i.key())
            # print(str(i.val()["cat_id"]),cat_id)
            if str(i.val()["cat_id"]) == id:

                if 'myfile' in request.FILES:
                    file = request.FILES['myfile']
                    file_save = default_storage.save(file.name, file)
                    storage.child( "main_category/" + file.name+str(id)).put(file.name)
                    delete = default_storage.delete(file.name)
                    img_url = storage.child("main_category/" + file.name+str(id)).get_url(None)
                    print(img_url)
                else:
                    img_url = i.val()["image"]

                d={"heading":heading,"desc":desc,"cat_id":i.val()["cat_id"],"image":img_url}
                # print("main",d)
                database.child("main_category").child(i.key()).update(d)
                break
                
    elif _type == "sub_category":
        print("sub",id)
        for i in database.child("sub_category").get().each():
            if str(i.val()["sub_cat_id"]) == id:
                if 'myfile' in request.FILES:
                    file = request.FILES['myfile']
                    file_save = default_storage.save(file.name, file)
                    storage.child( "sub_category/" + file.name+str(id)).put(file.name)
                    delete = default_storage.delete(file.name)
                    img_url = storage.child("sub_category/" + file.name+str(id)).get_url(None)
                    print(img_url)
                else:
                    img_url = i.val()["image"]

                d={"heading":heading,"blog":desc,"cat_id":main_cat,"sub_cat_id":i.val()["sub_cat_id"],"image":img_url}
                database.child("sub_category").child(i.key()).update(d)
                print("sub",main_cat,d)
                break
    
    elif _type == "sub_sub_category":
        print("sub_sub",id)
        for i in database.child("sub_sub_category").get().each():
            if str(i.val()["sub_sub_cat_id"]) == id:
                d={"heading":heading,"sub_cat_id":main_cat,"sub_sub_cat_id":i.val()["sub_sub_cat_id"]}
                database.child("sub_sub_category").child(i.key()).update(d)
    return objlist(request,_type)
    # return HttpResponse('edit category')




def add_category(request):


    if request.method == 'POST' :
        
        _type = request.POST.get('submit') 
        heading = request.POST.get('heading')
        desc = request.POST.get('desc')
        
        print(desc)
        
        if _type == "main_category":
            cat_id = database.child("cat_id").get().val()+1
            database.update({"cat_id":cat_id})

            file = request.FILES['myfile']
            file_save = default_storage.save(file.name, file)
            storage.child( "main_category/" + file.name+str(cat_id)).put(file.name)
            delete = default_storage.delete(file.name)
            img_url = storage.child("main_category/" + file.name+str(cat_id)).get_url(None)
            print(img_url)

            d={"heading":heading,"desc":desc,"cat_id":cat_id,"image":img_url}
            database.child("main_category").push(d)
        elif _type == "sub_category":        
            answer = request.POST['dropdown']
            # print(heading,desc,file,answer)
            sub_cat_id = database.child("sub_cat_id").get().val()+1
            database.update({"sub_cat_id":sub_cat_id})

            for i in database.child("main_category").get().each():
                if i.val()["heading"]==answer:
                    cat_id = i.val()["cat_id"]
                    break
            # PIC SAVE
            file = request.FILES['myfile']
            file_save = default_storage.save(file.name, file)
            storage.child( "sub_category/" + file.name+str(sub_cat_id)).put(file.name)
            delete = default_storage.delete(file.name)
            img_url = storage.child("sub_category/" + file.name+str(sub_cat_id)).get_url(None)
            print(img_url)
            d={"heading":heading,"blog":desc,"sub_cat_id":sub_cat_id,"cat_id":cat_id,"image":img_url}
            database.child("sub_category").push(d)

        
        elif _type == "sub_sub_category":
            answer = request.POST['dropdown']
            # print(heading,desc,file,answer)
            sub_sub_cat_id = database.child("sub_sub_cat_id").get().val()+1
            database.update({"sub_sub_cat_id":sub_sub_cat_id})

            for i in database.child("sub_category").get().each():
                if i.val()["heading"]==answer:
                    sub_cat_id = i.val()["sub_cat_id"]
                    break

            d={'heading':heading,'sub_sub_cat_id':sub_sub_cat_id,'sub_cat_id':sub_cat_id}
            database.child("sub_sub_category").push(d)

        return objlist(request,_type)
        
    else:
        return render(request,"admin_home.html")   
