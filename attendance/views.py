from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request,"index.html")


def admin_dashboard(request):
    return render(request,"admin/admin_dashboard.html")