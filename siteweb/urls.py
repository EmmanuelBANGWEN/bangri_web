
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('about/', views.about_view, name='about_view'),
    path('blog/', views.blog_view, name='blog_view'),
    path('contact/', views.contact_view, name='contact_view'),
    path('services/', views.services_view, name='services_view'),
    path('testimonials/', views.testimonials_view, name='testimonials_view'),
    path('blog_details/', views.blog_details, name='blog_details'),
    path('category/<slug:category>/', views.category_view, name='category_view'),
    path('tag/<slug:tag_slug>/', views.tag_view, name='tag_view'),
    path('blog_details/<int:year>/<int:month>/<int:day>/<slug>/', views.blog_details_view, 
                                                    name='blog_details_view'),
    path('search/', views.post_search, name='post_search'),
    path('/', views.subscribe_view, name='subscribe_view'),
    path('send_newsletter/', views.send_newsletter_view, name='send_newsletter_view'),
    path('contact/', views.contact, name='contact'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('developpement_logiciel/', views.developpement_logiciel, name='developpement_logiciel'),
    path('analyse_donnees/', views.analyse_donnees, name='analyse_de_données'),
    path('consultation/', views.consultation, name='consultation'),
    path('marketing_digital/', views.marketing_digital, name='marketing_digital'),
    path('assistance/', views.assistance, name='assistance'),
    path('consultations/', views.consultation_view, name='consultation_view'),
    path('contacts/', views.contact_view, name='contact_view'),
    





]