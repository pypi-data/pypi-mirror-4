# Create your views here.
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import New

def list (request):
    news_list = New.objects.get_active()  
    paginator = Paginator(news_list, 4)
    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        news = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        news = paginator.page(paginator.num_pages)
    return render(request,
                  'news/news_index.html', 
                  {'news': news} , 
                  content_type='text/html')  

def new_detail(request, id, slug):
    new = New.objects.get(pk=id) 
    return render(request,
                  'news/new_detail.html', 
                  {'new': new} , 
                  content_type='text/html')
