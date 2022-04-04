# importing module
import logging
 # Create and configure logger
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 # Creating an object
logger = logging.getLogger()
 # Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

from django.core.files import storage
from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from pyasn1.type.univ import ObjectIdentifier 
import pyrebase
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage,default_storage
from django.contrib import messages
import requests

from django.conf import settings
from django.core.mail import send_mail

# firebase database
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

firebase = pyrebase.initialize_app(firebaseConfig)
database = firebase.database()
storage = firebase.storage()
# firebase database




# razorpay
import razorpay
from django.conf import settings
from django.http import HttpResponseBadRequest

import json
from django.views.decorators.csrf import csrf_exempt
# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
# razorpay

def travel(request):
    data = json.loads(request.GET.get('dataobj', ''))
    print(data)
    idd = database.child("travel").child("id").get().val()+1
    database.child("travel").update({"id":idd})
    data["id"] = idd
    emailorphone = request.session["user_email"]
    for i in database.child("user").get().each():
        if emailorphone == i.val()["email"] or emailorphone == i.val()["phno"]:
            data["user"] = i.val()
            break
    data["status"] = False
    data["readUnread"] = False
    if data["serviceType"] == "Air Ticket":
        database.child("travel").push(data)
        subject = f'Dear Decent Services'
        message = f'You have received a new service request in travel.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['servicesdecent.jamshedpur@gmail.com']
        z = send_mail( subject, message, email_from, recipient_list )
        print(z)
        return JsonResponse({"status":"AirTicketSuccess"})
    else:
        database.child("travel").push(data)
        subject = f'Dear Decent Services'
        message = f'You have received a new service request in travel.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['servicesdecent.jamshedpur@gmail.com']
        z = send_mail( subject, message, email_from, recipient_list )
        print(z)
        return JsonResponse({"status":"travelSuccess"})

@csrf_exempt
def buisnessLicence(request):
    if request.method == 'POST' and request.is_ajax():
        serviceType = request.POST.get("serviceType")

        idd = database.child("buisnessLicence").child("id").get().val()+1
        database.child("buisnessLicence").update({"id":idd})
        i=0
        imgUrlList = []
        while(request.FILES.get('file'+str(i))!=None):
            file = request.FILES.get('file'+str(i))               # Get the file data from
            file_save = default_storage.save(file.name, file)
            storage.child( "buisnessLicence/"+str(idd)+"/" + file.name).put(file.name)
            delete = default_storage.delete(file.name)
            imgUrl = storage.child( "buisnessLicence/"+str(idd)+"/" + file.name).get_url(None)
            imgUrlList.append(imgUrl)
            i+=1
        data = {"docs":imgUrlList,"id":idd,"serviceType":serviceType}
        
        emailorphone = request.session["user_email"]
        for i in database.child("user").get().each():
                if emailorphone == i.val()["email"] or emailorphone == i.val()["phno"]:
                    data["user"] = i.val()
                    break
        data["status"] = False
        data["readUnread"] = False
        database.child("buisnessLicence").push(data)
        print(imgUrlList)
        subject = f'Dear Decent Services'
        message = "You have received a new service request in Buisness License."
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['servicesdecent.jamshedpur@gmail.com']
        z = send_mail( subject, message, email_from, recipient_list )
        print(z)
        return JsonResponse({"info":"buisnessLicenceSuccess"})
    else:
        return JsonResponse({"info":"buisnessLicenceFailure"})



@csrf_exempt
def governmentServicesPaymentHandler(request):
        # only accept POST request.
    if request.method == "POST":
        try:
        
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            print(params_dict)
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            logger.info("ok1")
            if result is None:
                try:
                    logger.info("ok2")
                    amount = request.session["amount"]
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    logger.info("ok3")
                    # capture the payemt
                    if request.session["txnInfo"]["serviceType"] in ["Basic Computer Course","British English Council Course"]:
                        idd = database.child("educationPayment").child("id").get().val()+1
                        database.child("educationPayment").update({"id":idd})
                        fileNames = request.session["gsFileNames"]
                        imgUrlList = []
                        print(fileNames)
                        logger.info("ok4")
                        for fileName in fileNames:
                            storage.child( "educationPayment/"+str(idd)+"/" + fileName).put(fileName)
                            delete = default_storage.delete(fileName)
                            imgUrl = storage.child( "educationPayment/"+str(idd)+"/" + fileName).get_url(None)
                            imgUrlList.append(imgUrl)
                            # print(img_url1)
                            
                        request.session["txnInfo"]["docs"] = imgUrlList  
                        request.session["txnInfo"]["id"] = idd
                        request.session["txnInfo"]["razorpay_payment_id"] = payment_id
                        emailorphone = request.session["user_email"]
                        logger.info("ok5")

                        for i in database.child("user").get().each():
                            if emailorphone == i.val()["email"] or emailorphone == i.val()["phno"]:
                                request.session["txnInfo"]["user"] = i.val()
                                break
                        request.session["txnInfo"]["status"] = False
                        request.session["txnInfo"]["readUnread"] = False
                        
                        database.child("educationPayment").push(request.session['txnInfo'])
                      
                    else:
                        logger.info("ok6")
                        idd = database.child("governmentServices").child("id").get().val()+1
                        database.child("governmentServices").update({"id":idd})
                        fileNames = request.session["gsFileNames"]
                        imgUrlList = []
                        print(fileNames)
                        for fileName in fileNames:
                            storage.child( "governmentServices/"+str(idd)+"/" + fileName).put(fileName)
                            delete = default_storage.delete(fileName)
                            imgUrl = storage.child( "governmentServices/"+str(idd)+"/" + fileName).get_url(None)
                            imgUrlList.append(imgUrl)
                            # print(img_url1)
                            
                        request.session["txnInfo"]["docs"] = imgUrlList  
                        request.session["txnInfo"]["id"] = idd
                        request.session["txnInfo"]["razorpay_payment_id"] = payment_id
                        emailorphone = request.session["user_email"]
                        for i in database.child("user").get().each():
                            if emailorphone == i.val()["email"] or emailorphone == i.val()["phno"]:
                                request.session["txnInfo"]["user"] = i.val()
                                break
                        request.session["txnInfo"]["status"] = False
                        request.session["txnInfo"]["readUnread"] = False
                        database.child("governmentServices").push(request.session['txnInfo'])

                    


                    subject = f'Dear Decent Services'
                    message = f'You have received a new service request in payment.'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = ['servicesdecent.jamshedpur@gmail.com']
                    z = send_mail( subject, message, email_from, recipient_list )
                    logger.info("email send1")
                    print(z)
                    # render success page on successful caputre of payment
                    return HttpResponse("<a href='/'>Home</a><h1 style='text-align:center;color:green;'>Payment Successfull</h1><h2 style='text-align:center;'>We have successfully received your document and will contact you as soon as possible!!!</h2>")
                except:
                        logger.info("email not send1")
                        fileNames = request.session["gsFileNames"]
                        for fileName in fileNames:
                            delete = default_storage.delete(fileName)
                        # if there is an error while capturing payment.
                        return HttpResponse("<a href='/'>Home</a><h1 style='text-align:center;color:green;'>Payment Successfull</h1><h2 style='text-align:center;'>We have successfully received your document and will contact you as soon as possible!!!</h2>")
            else:
                fileNames = request.session["gsFileNames"]
                for fileName in fileNames:
                    delete = default_storage.delete(fileName)
                # if signature verification fails.
                return HttpResponse("<a href='/'>Home</a><h1 style='text-align:center;color:red;'>Payment Failed2</h1>")
        except:
            fileNames = request.session["gsFileNames"]
            for fileName in fileNames:
                delete = default_storage.delete(fileName)
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        fileNames = request.session["gsFileNames"]
        for fileName in fileNames:
            delete = default_storage.delete(fileName)
    # if other than POST request is made.
        return HttpResponseBadRequest()
@csrf_exempt
def governmentServicesPayment(request):
    if request.method == 'POST' and request.is_ajax():
        serviceType = request.POST.get("serviceType")
        amount = request.POST.get("amount")

        i=0
        fileNames=[]
        while(request.FILES.get('file'+str(i))!=None):
            file = request.FILES.get('file'+str(i))               # Get the file data from
            file_save = default_storage.save(file.name, file)
            fileNames.append(file.name)
            i+=1
        request.session["gsFileNames"] = fileNames
        # print("rehan Payment")
        # print(fileNames)
        request.session["amount"] = amount

        # print(serviceType,amount,type(amount))

        # Create a Razorpay Order
        currency = 'INR'
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                        currency=currency,
                                                        payment_capture='0'))

        d={"amount":float(amount)/100,"serviceType":serviceType,"razorpay_order_id":razorpay_order['id']}
        request.session['txnInfo'] = d
        

        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = 'governmentServicesPaymentHandler'

        # we need to pass these details to frontend.
        context = {}
        context['order_id'] = razorpay_order_id
        context['key'] = settings.RAZOR_KEY_ID
        context['amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url
        context['name'] = "Dj Razorpay"
        # print(razorpay_order)
     
        return JsonResponse(context)
    else:
        return JsonResponse({"info":"GSPaymentFailure"})
def subSubCat(request):
    _type = request.GET.get("type")
    print(_type)
    l = []
    for i in database.child("main_category").get().each():
        if i.val()["cat_id"]!=-1:
            l.append(i.val())

    
    if _type == "Vehicle Insurance":
        return render(request,"tan_app_temp/insurance/vehicle_insurance.html",context={'l':l})

    elif _type == "Health Insurance":
        return render(request,"tan_app_temp/insurance/health_insurance.html",context={'l':l})
    elif _type == "Term Insurance":
        return render(request,"tan_app_temp/insurance/term_insurance.html",context={'l':l})
    
    elif _type == "Voter Card":
        return render(request,"tan_app_temp/governmentServices/voterCard.html",context={'l':l})
    elif _type == "Pan Card":
        return render(request,"tan_app_temp/governmentServices/panCard.html",context={'l':l})
    elif _type == "Ration Card":
        return render(request,"tan_app_temp/governmentServices/rationCard.html",context={'l':l})
    elif _type == "Residential Certificate":
        return render(request,"tan_app_temp/governmentServices/residentialCertificate.html",context={'l':l})
    elif _type == "Income Certificate":
        return render(request,"tan_app_temp/governmentServices/incomeCertificate.html",context={'l':l})
    elif _type == "Driving Licence":
        return render(request,"tan_app_temp/governmentServices/drivingLicence.html",context={'l':l})
    elif _type == "Life Certificate for Pensioner":
        return render(request,"tan_app_temp/governmentServices/lifeCertificateForPensioner.html",context={'l':l})
    elif _type == "Online Mutation Application":
        return render(request,"tan_app_temp/governmentServices/onlineMutationApplication.html",context={'l':l})
    elif _type == "Bhoomi Lagaan / Land Tax":
        return render(request,"tan_app_temp/governmentServices/landTax.html",context={'l':l})

    elif _type == "Food Licence (For Small Buisness)":
        return render(request,"tan_app_temp/buisnessLicence/foodLicence.html",context={'l':l})
    elif _type == "Trade Licence":
        return render(request,"tan_app_temp/buisnessLicence/tradeLicence.html",context={'l':l})
    elif _type == "Shops & Establishment Licence":
        return render(request,"tan_app_temp/buisnessLicence/shops&EstablishmentLicence.html",context={'l':l})
    elif _type == "MSME / UDYAM Registration (UDYOG Aadhar)":
        return render(request,"tan_app_temp/buisnessLicence/UDYAMRegistration.html",context={'l':l})
    elif _type == "GST Registration":
        return render(request,"tan_app_temp/buisnessLicence/GSTRegistration.html",context={'l':l})
    elif _type == "Digital Signature":
        return render(request,"tan_app_temp/buisnessLicence/digitalSignature.html",context={'l':l})
    elif _type == "PF Registration":
        return render(request,"tan_app_temp/buisnessLicence/PFRegistration.html",context={'l':l})
    elif _type == "ESI Registration":
        return render(request,"tan_app_temp/buisnessLicence/ESIRegistration.html",context={'l':l})
    
    elif _type == "Railway Ticket":
        return render(request,"tan_app_temp/travel/railTicket.html",context={'l':l})
    elif _type == "Air Ticket":
        return render(request,"tan_app_temp/travel/airTicket.html",context={'l':l})
    
    elif _type == "British English Council Course":
        return render(request,"tan_app_temp/education/britishEnglishCouncil.html",context={'l':l})
    elif _type == "Basic Computer Course":
        return render(request,"tan_app_temp/education/basicComputerCourse.html",context={'l':l})
    else:
        return JsonResponse({"status":"insurance"})

def saveQuotation(request):
    
    if request.is_ajax():
        lis = request.GET.getlist('lis[]')
        serviceType = request.GET.get("serviceType")
        l=[]
    
        q = database.child("quotation").child("id").get().val()+1
        database.child("quotation").update({"id":q})
        emailorphone = request.session["user_email"]
        for i in database.child("user").get().each():
            if i.val()["email"] == emailorphone or i.val()["phno"] == emailorphone:
                l.append({"user":i.val()})   
                break 
            
           
        for i in lis:
            r = json.loads(i)
            l.append(r)
        l.append({"serviceType":serviceType,"id":q,"status":False,"readUnread":False})
        database.child("quotation").push(l)
        subject = f'Dear Decent Services'
        message = "You have received a new service request in quotation."
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['servicesdecent.jamshedpur@gmail.com']
        z = send_mail( subject, message, email_from, recipient_list )
        print(z)
        return JsonResponse({"status":"successSaveQuotation"})
        
    return JsonResponse({"status":"Not an ajax request"})

    


def status(request):
    return HttpResponse("<a href='/'>Home</a><h1 style='text-align:center;'>Documents Submitted Successfully</h1><h2 style='text-align:center;color:green;'>We have successfully received your document and will contatct you as soon as possible!!!</h2>");
    
def saveImage(request):
    q = database.child("quotation").child("id").get().val()+1
    
    img_url1=""
    if "myfile1" in request.FILES:
        file = request.FILES['myfile1']
        file_save = default_storage.save(file.name, file)
        storage.child( "quotation/" + file.name+str(q)).put(file.name)
        delete = default_storage.delete(file.name)
        img_url1 = storage.child("quotation/" + file.name+str(q)).get_url(None)
        imgName1 = file.name+str(q)
        # print(img_url1)

    if "myfile2" in request.FILES:
        file = request.FILES['myfile2']
        file_save = default_storage.save(file.name, file)
        storage.child( "quotation/" + file.name+str(q)+str(q)).put(file.name)
        delete = default_storage.delete(file.name)
        img_url2 = storage.child("quotation/" + file.name+str(q)+str(q)).get_url(None)
        imgName2 = file.name+str(q)+str(q)
        # print(img_url2)
    else:
        return HttpResponse("<a href='http://127.0.0.1:8000/insurance/Vehicle%20Insurance'>Home</a><h1 style='text-align:center;'>Owner Book is Mendatory...</h1>")
   
    database.child("quotation").update({"id":q})
    emailorphone = request.session["user_email"]
    
    for i in database.child("user").get().each():
        if i.val()["email"] == emailorphone or i.val()["phno"] == emailorphone:
            
            serviceType = "Vehicle Insurance"
            if img_url1!="":
                d = {"id":q,"user":i.val(),"previousInsurancePaper":img_url1,"ownerBook":img_url2,"imgName1":imgName1,"imgName2":imgName2,"serviceType":serviceType,"status":False,"readUnread":False}
            else:
                d = {"id":q,"user":i.val(),"ownerBook":img_url2,"imgName2":imgName2,"serviceType":serviceType,"status":False,"readUnread":False}
            
            database.child("quotation").push(d)
            break
    return HttpResponse("<a href='/'>Home</a><h1 style='text-align:center;'>Documents Submitted Successfully</h1><h2 style='text-align:center;color:green;'>We have successfully received your document and will contatct you as soon as possible!!!</h2>")




def payment(request):
    if request.is_ajax():
        if request.GET.get('niche') == "vehicleInsurance":
            _type = request.GET.get("type")
            tov = request.GET.get("tov")
            cc = request.GET.get("cc")
            pa = request.GET.get("pa")
            amount = request.GET.get("amount")
            request.session["amount"] = amount

            print(_type+tov+cc+pa+amount)
            
        currency = 'INR'
        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                        currency=currency,
                                                        payment_capture='0'))

        d={'type':_type,"typeOfVehicle":tov,"cc":cc,"PA":pa,"amount":float(amount)/100,"razorpay_order_id":razorpay_order['id'],"serviceType":"VehicleInsurance"}
        request.session['txnInfo'] = d
       

        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = 'paymenthandler'

        # we need to pass these details to frontend.
        context = {}
        context['order_id'] = razorpay_order_id
        context['key'] = settings.RAZOR_KEY_ID
        context['amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url
        context['name'] = "Dj Razorpay"
        print(razorpay_order)
        return JsonResponse(context)
        # return render(request, 'tan_app_temp/payment/index.html', context=context)


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):

    # only accept POST request.
    if request.method == "POST":
        try:
        
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is None:
                amount = request.session["amount"]
                try:

                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)

                    print("akhterrehan")
                    vi_id = database.child("insurancePayment").child("vi_id").get().val()+1
                    database.child("insurancePayment").update({"vi_id":vi_id})
                    
                    request.session["txnInfo"]["id"] = vi_id
                    request.session["txnInfo"]["razorpay_payment_id"] = payment_id
                    emailorphone = request.session["user_email"]
                    for i in database.child("user").get().each():
                        if emailorphone == i.val()["email"] or emailorphone == i.val()["phno"]:
                            request.session["txnInfo"]["user"] = i.val()
                            break
                    print(request.session["txnInfo"],request.session["user_email"])
                    request.session["txnInfo"]["status"] = False
                    request.session["txnInfo"]["readUnread"] = False
                    database.child("insurancePayment").push(request.session['txnInfo'])
                    subject = f'Dear Decent Services'
                    message = f'You have received a new service request.'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = ['servicesdecent.jamshedpur@gmail.com']
                    z = send_mail( subject, message, email_from, recipient_list )
                    print(z)
                    # render success page on successful caputre of payment
                    return HttpResponse("<a href='/'>Home</a><h1 style='text-align:center;color:green;'>Payment Received Successfully</h1><h2 style='text-align:center;'>We have successfully received your document and will contact you as soon as     possible!!!</h2>")
                except:
                        # if there is an error while capturing payment.
                        return HttpResponse("<a href='/'>Home</a><h1 style='text-align:center;color:red;'>Payment Failed3</h1>")
            else:

                # if signature verification fails.
                return HttpResponse("<a href='/'>Home</a><h1 style='text-align:center;color:red;'>Payment Failed4</h1>")
        except:

            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
    # if other than POST request is made.
        return HttpResponseBadRequest()
# ..................razorpay...........











# Create your views here.

def parent(request):
    return render(request,"child.html")






@csrf_exempt
def blog(request,id=None):
   
    if request.is_ajax():
        
        blogId = int(request.POST.get('blogId'))
        print(blogId,"rehan")
        heading = ""
        blog = []
        for i in database.child("blog").get().each():
            if i.val()["blogId"] == blogId:
                blog = i.val()["content"]
                break
        return JsonResponse({"info":"successBlog","blog":blog})
     
    l = []
    for i in database.child("main_category").get().each():
        if i.val()["cat_id"]!=-1:
            l.append(i.val())

    id = int(request.GET.get("blogId",-1))
    lis = []
    reqLis = []

    test = {}
    for i in database.child("blog").get().each():
        if type(i.val())!=int:
            if i.val()["categoryId"] in test:
                test[i.val()["categoryId"]] += [[i.val()["blogId"],i.val()["heading"]]]
            else:
                test[i.val()["categoryId"]] = [[i.val()["blogId"],i.val()["heading"]]]
            lis.append(i.val())

    for i in database.child("sub_category").get().each():
        if type(i.val())!=int:
            if i.val()["sub_cat_id"] in test:
                test[i.val()["heading"], i.val()["sub_cat_id"]] = test[i.val()["sub_cat_id"]]
                del test[i.val()["sub_cat_id"]]

    
    for i in database.child("main_category").get().each():
        if type(i.val())!=int:
            if i.val()["cat_id"] in test:
                test[i.val()["heading"], i.val()["cat_id"]] = test[i.val()["cat_id"]]
                del test[i.val()["cat_id"]]

    for i in test:
        if type(i)== int:
            test["others",i] = test[i]
            del test[i]
            break
        
    for i in database.child("blog").get().each():
        if type(i.val())!=int and id == i.val()["categoryId"]:
            reqLis.append(i.val())

    
    return render(request,"tan_app_temp/blog.html",context={'l':l,'lis':test,'reqLis':reqLis    })




def sub_category(request):
    id = int(request.GET.get("id"))
    
    lis = []
    # info = ""
    for i in database.child("sub_category").get().each():
       
        if i.val()["cat_id"] == id:
            lis.append(i.val())
            # if info=="" and "insurance" in (i.val()["heading"]).lower() :
            #     info = "insurance"
    # print(lis)

    l = []
    for i in database.child("main_category").get().each():
        if i.val()["cat_id"]!=-1:
            l.append(i.val())

    return render(request,"tan_app_temp/sub_category.html",context={'l':l,'lis':lis})

def showSubSubCat(request):
    idd = int(request.GET.get("sub_cat_id"))
    print(idd)
    l=[]
    for i in database.child("sub_sub_category").get().each():
        if i.val()["sub_cat_id"] == idd:
            l.append(i.val())
    print(l)
    return JsonResponse({"l":l})
    return HttpResponse("google")











# ........................ changePassword .......................


def verifyOtp(request):
    phno = request.GET.get('phno')
    otp = request.GET.get('otp')
    request.session['phno'] = phno
  
    print(type('otp'))
    for i in database.child("user").get().each():
        if type(i.val())!=int and i.val()["phno"] == phno:
            print(i.val()["phno"])
            url = "https://www.fast2sms.com/dev/bulk"
            payload = "sender_id=FSTSMS&message=Your OTP(One Time Password):-\n"+otp+"&language=english&route=p&numbers="+phno
            headers = {
            # 'authorization': "QrBK8fjst9axbG6IbCCcH2d3ZLV1j3aIl6SQMo5o9TGiPghqKgQIOwnoybQU",#rehan api
            'authorization': "qonk2CxERPXI2PJBCILTS4BETiGZpH5LS2jBhgsmbbpnMSIDJskEJXnhFXAS",#tanweer api
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
            }
            response = requests.request("POST", url, data=payload, headers=headers)
            print(response.text)

            return JsonResponse({"info":"success"})
            
    return JsonResponse({"info":"Mobile number is not registered."})

def changePassword(request):
    phno = request.session['phno']
    password = request.GET.get("password")
    print(password,phno,type(phno))
    for i in database.child("user").get().each():
        print(int(phno),int(i.val()['phno']),type(int(phno)),type(int(i.val()['phno'])))
        if type(i.val())!=int and phno == i.val()['phno']:
            print("match")
            database.child("user").child(i.key()).update({"password":password})
            return JsonResponse({"info":"Password Changed Successfully"})
     
    return JsonResponse({"info":"failure"})


# ........................ changePassword .......................









# ..........................Register Login Logout.................


def sendOtp(request):
    email = request.GET.get("email")
    phno = request.GET.get("phno")
    otp = request.GET.get("otp")
    info = request.GET.get("info")
    if info == "register":
        for i in database.child("user").get().each():
            if type(i.val())!=int:
                if i.val()["email"]==email:
                    return JsonResponse({"info":"Email ID is already registered"})
                elif i.val()["phno"]==phno:
                    return JsonResponse({"info":"Mobile no is already registered"})
            
    url = "https://www.fast2sms.com/dev/bulk"
    payload = "sender_id=FSTSMS&message=Your OTP(One Time Password):-\n"+otp+"&language=english&route=p&numbers="+phno
    headers = {
    'authorization': "QrBK8fjst9axbG6IbCCcH2d3ZLV1j3aIl6SQMo5o9TGiPghqKgQIOwnoybQU",
    'Content-Type': "application/x-www-form-urlencoded",
    'Cache-Control': "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    # print(response.text)
    return JsonResponse({"info":"success"})

def register(request):
    if request.is_ajax():
        name = request.GET.get("name")
        email = request.GET.get("email")
        whatsappPhno = request.GET.get("whatsappPhno")
        password = request.GET.get("password")
        phno = request.GET.get("phno")
        otp = request.GET.get("otp")

        user_id = database.child("user").child("user_id").get().val()+1
        database.child("user").update({"user_id":user_id})
        # print(name,email,password,phno)
                
        data={'id':user_id,'name':name,'email':email,'password':password,'phno':phno,'whatsappPhno':whatsappPhno,'status':False}
        database.child("user").push(data)
        return JsonResponse({"info":"User Registered Succesfully"})
    return HttpResponse("register")

def userSessionCheck(request):
    if request.is_ajax():
        if "user_email" in request.session:
            return JsonResponse({"info":"success"})
        else:
            return JsonResponse({"info":"failure"})
def login(request):
    if request.is_ajax():
        email = request.GET.get("emailorphone")
        password = request.GET.get("password")
        print(email,password)

        for i in database.child("user").get().each():
            if type(i.val())!=int and (i.val()["email"]==email or i.val()["phno"]==email) and i.val()["password"]==password:
                request.session["user_email"] = email
                request.session["user_name"] = i.val()["name"]
                return JsonResponse({"info":"Login Successful"+i.val()["name"]})
        else:
            return JsonResponse({"info":"email or password does not match"})
    else:
        return HttpResponse("Invalid Credentials")


def logout(request):
    if request.is_ajax():
        if "amount" in request.session:
            del request.session["amount"]
        if "user_email" in request.session:
            del request.session["user_email"]
        if "user_name" in request.session:
            del request.session["user_name"]
        if "phno" in request.session:
            del request.session["phno"]
        
        if "txnInfo" in request.session:
            print(request.session["txnInfo"])
            
            del request.session["txnInfo"]
        return JsonResponse({"info":"success"})
  
    else:
        return HttpResponse("<h1>Bad Request<h1>")
     
    


# ..........................Register Login Logout.................



def home(request):  
    # print(logging)
    # logger.info("ok")
    # subject = 'welcome to Decent Services'
    # message = f'Hi Tanweer, thank you for registering in decent services.'
    # email_from = settings.EMAIL_HOST_USER
    # recipient_list = ['decentcsc@gmail.com']
    # send_mail( subject, message, email_from, recipient_list )
    # user_count = database.child("user_count").get().val()+1
    # database.update({"user_count":user_count})
    # for i in database.child("educationPayment").get().each():
    #     if type(i.val())!=int:
    #         database.child("educationPayment").child(i.key()).update({"readUnread":False})
    l = []
    subCategory = []
    for i in database.child("main_category").get().each():
        if type(i.val())!=int:
            l.append(i.val())
    for i in database.child("sub_category").get().each():
        if type(i.val())!=int:
            subCategory.append(i.val())


    print(len(subCategory))
    return render(request,"tan_app_temp/home.html",context={'l':l,'subCategory':subCategory})

def about(request):
    return render(request,"tan_app_temp/aboutUs.html")

def contact(request):
    return render(request,"tan_app_temp/contactUs.html")