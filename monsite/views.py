# from django.shortcuts import render

# def home_view(request):
#     return render(request, 'monsite/index.html')

# monsite/views.py
from django.shortcuts import render

def admin_dashboard_view(request):
    # Logique pour le tableau de bord de l'admin
    return render(request, 'siteweb/admin_dashboard.html')
