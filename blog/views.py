from django.shortcuts import render
from django.http import HttpResponse
from .models import Blogpost

def index(request):
	myposts = Blogpost.objects.all()
	print(myposts)
	params = {'myposts':myposts}
	return render(request, 'blog/index.html', params)

def blogpost(request, id):
	post = Blogpost.objects.filter(post_id=id)[0]
	print(post)
	params = {'post':post}
	return render(request, 'blog/blogpost.html',params)
