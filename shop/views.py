from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from PayTm import Checksum
MERCHANT_KEY = 'Your-Merchant-Key-Here'

def index(request):
	allProds = []
	catprods = Product.objects.values('category', 'id')
	cats = {item['category'] for item in catprods}
	for cat in cats:
		prod = Product.objects.filter(category=cat)
		n = len(prod)
		nSlides = n // 4 + ceil((n / 4) - (n // 4))
		allProds.append([prod, range(1, nSlides), nSlides])
	params = {'allProds':allProds}
	return render(request, 'shop/index.html', params)

def searchMatch(query, item):
	if query.lower() in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
		return True
	else:
		return False

def search(request):
	query = request.GET.get('search')
	allProds = []
	catprods = Product.objects.values('category', 'id')
	cats = {item['category'] for item in catprods}
	for cat in cats:
		prodtemp = Product.objects.filter(category=cat)
		prod = [item for item in prodtemp if searchMatch(query, item)]

		n = len(prod)
		nSlides = n // 4 + ceil((n / 4) - (n // 4))
		if len(prod) != 0:
			allProds.append([prod, range(1, nSlides), nSlides])
	params = {'allProds':allProds, 'msg': ''}

	if len(allProds) == 0 or len(query)<4:
		params = {'msg': 'Please make sure to enter relevant search query'}

	return render(request, 'shop/search.html', params)

def about(request):
	return render(request, 'shop/about.html')


def contact(request):
	if request.method == 'POST':
		name = request.POST.get('name','')
		email = request.POST.get('email','')
		phone = request.POST.get('phone','')
		desc = request.POST.get('desc','')
		print(name, email, phone, desc)
		contact = Contact(name=name, email=email, phone=phone, desc=desc)
		contact.save()
		messages.success(request, 'Your request has been submitted, we will get back to you soon.')
	return render(request, 'shop/contact.html')


def tracker(request):
	if request.method == 'POST':
		orderid = request.POST.get('orderid','')
		email = request.POST.get('email','')

		try:
			order = Orders.objects.filter(order_id=orderid, email=email)
			if len(order)>0:
				update = OrderUpdate.objects.filter(order_id=orderid)
				updates = []
				for item in update:
					updates.append({'text': item.update_desc, 'time':item.timestamp})
					response = json.dumps({"status": "success","updates":updates, "itemsJson":order[0].items_json}, default=str)
				return HttpResponse(response)

			else:
				return HttpResponse('{"status":"noitem"}')

		except Exception as e:
			return HttpResponse('{"status":"error"}')

	return render(request, 'shop/tracker.html')


def products(request, myid):
	product = Product.objects.filter(id=myid)
	params = {'product': product[0]}
	return render(request, 'shop/productview.html',params)


def checkout(request):
	if request.method == 'POST':
		items_json = request.POST.get('itemsJson','')
		name = request.POST.get('name','')
		amount = request.POST.get('amount','')
		email = request.POST.get('email','')
		address = request.POST.get('address1','') + " " + request.POST.get('address2','')
		city = request.POST.get('city','')
		state = request.POST.get('state','')
		zip_code = request.POST.get('zip_code','')
		phone = request.POST.get('phone','')

		order = Orders(items_json=items_json, name=name, amount=amount, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone)
		order.save()
		update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed.")
		update.save()
		thank = True
		id = order.order_id
		param_dict={

			'MID': 'Your-Merchant-ID-Here',
			'ORDER_ID': str(order.order_id),
			'TXN_AMOUNT': str(amount),
			'CUST_ID': email,
			'INDUSTRY_TYPE_ID': 'Retail',
			'WEBSITE': 'WEBSTAGING',
			'CHANNEL_ID': 'WEB',
			'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

		}
		param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)

		return render(request, 'shop/paytm.html', {'param_dict':param_dict})
		# return render(request, 'shop/checkout.html', params)
		# request paytm to  transfer the amount to your account
		
	return render(request, 'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
	#post request
	form = request.POST
	response_dict = {}
	for i in form.keys():
		response_dict[i] = form[i]
		if i == 'CHECKSUMHASH':
			checksum = form[i]

	verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
	if verify:
		if response_dict['RESPCODE'] == '01':
			print('order successful')
		else:
			print('order was not successful because' + response_dict['RESPMSG'])


	return render(request, 'shop/paymentstatus.html', {'response':response_dict})
