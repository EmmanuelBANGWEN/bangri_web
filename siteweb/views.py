from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from .models import Post, Comment, Category, Subscriber
from .forms import CommentForm, SearchPost, SubscriptionForm, ConsultationForm, ContactForm
from taggit.models import Tag
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Count
from django.urls import reverse


def home_view(request):
    recent_posts = Post.objects.order_by('-published')[:3]
    return render(request, 'siteweb/index.html', {'recent_posts': recent_posts})

def about_view(request):
    return render(request, 'siteweb/about.html')

def category_view(request, category):
    categories = Category.objects.all()
    if category:
        category = get_object_or_404(Category, slug=category)
        posts = Post.objects.filter(category=category).order_by('published')
    return render(request, 'siteweb/category.html', {
        'category': category,
        'posts': posts,
        'categories' : categories,
    })
def tag_view(request, tag_slug):
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])

    return render(request, 'siteweb/tag.html', {
        'tag_slug': tag_slug,
        'posts': posts,
        'tag' : tag,

    })
def blog_details_view(request, year: int, month: int, day: int, slug: str, category=None, tag_slug=None):
    post = get_object_or_404(Post, slug=slug, statut='published', published__year=year, 
                             published__month=month, published__day=day)
    comments = post.comments.filter(parent__isnull=True).prefetch_related('replies')
    form = CommentForm()

    categories = Category.objects.all()
    tags = Tag.objects.all()

    posts = Post.objects.all()

    # Retirer ceci car tu n'as pas besoin d'un seul profil générique
    # profile = Profile.objects.all()

    if category:
        category = get_object_or_404(Category, slug=category)
        posts = posts.filter(category=category).order_by('published')
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    new_comment = None
    if request.method =='POST':
        if request.user.is_authenticated:

            form = CommentForm(request.POST)

            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.post = post
                new_comment.author = request.user
                parent_id = request.POST.get('parent_id')
                if parent_id:
                    parent_comment = Comment.objects.get(id=parent_id)
                    new_comment.parent = parent_comment
                new_comment.save()
                return redirect(reverse('blog_details_view', kwargs={
                    'year': year,
                    'month': month,
                    'day': day,
                    'slug': slug
                }))
        else:
            messages.error(request, "Veillez vous connecter ! ")
            return redirect('login_view')
    else:
        comment_form = CommentForm()
    posts_tag_id = post.tags.values_list("id", flat=True)
    similar_post = Post.objects.filter(tags__in=posts_tag_id).exclude(id=post.id)
    similar_post = similar_post.annotate(same_tags=Count('tags')).order_by('-same_tags', '-published')[:4]
    recent_posts = Post.objects.all().exclude(id=post.id)
    recent_posts = recent_posts.order_by('-published')[:3]
        
    return render(request, 'siteweb/blog-details.html',  {
                                                    'post': post,
                                                    'comments': comments,
                                                    'form': form,
                                                    'new_comment': new_comment,
                                                    'comment_form': comment_form,   
                                                    'categories': categories,
                                                    'category': category,
                                                    'tags': tags,
                                                    'similar_post': similar_post,
                                                    'recent_posts': recent_posts,
                                                    })


def blog_view(request):
    posts = Post.published_posts.all()
    
    paginator = Paginator(posts, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger :
        posts = paginator.page(1)
    except EmptyPage :
        posts = paginator.page(paginator.num_pages)
    context = {
        'posts' : posts,
        'page'  : page,
        
}
    return render(request, 'siteweb/blog.html', context)

def contact_view(request):
    return render(request, 'siteweb/contact.html')

def services_view(request):
    return render(request, 'siteweb/services.html')

def blog_details(request):
    return render(request, 'siteweb/services.html')


def testimonials_view(request):
    return render(request, 'siteweb/testimonials.html')

def post_search(request):
    query = None
    results = []
    search_form = SearchPost()

    if 'query' in request.GET:
        search_form = SearchPost(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            vector_search = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            query_search = SearchQuery(query)
            # results = Post.published_posts.annotate(
            #     search=vector_search, rank=SearchRank(vector_search,query_search)
            # ).filter(rank__gte=0.3).order_by('rank')
            results = Post.published_posts.annotate(
                                                    similarity=TrigramSimilarity("title", query),
                                                    ).filter(similarity__gt=0.1).order_by("-similarity")

    return render(request, 'siteweb/search.html', {
        'search_form': search_form,
        'query': query,
        'results': results,
    })

def subscribe_view(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have successfully subscribed to our newsletter.')
            return redirect('home_view')  # Remplace par l'URL de redirection souhaitée
    # else:
    #     form = SubscriptionForm()
    # return render(request, 'siteweb/subscribe.html', {'form': form})
    return render(request, 'siteweb/index.html')

def send_newsletter(subject, message):
    subscribers = Subscriber.objects.values_list('email', flat=True)
    # send_mail(subject, message, 'bikoyemmanuel531@gmail.com', list(subscribers))
    html_message = render_to_string('siteweb/newsletter_template.html', {'subject': subject, 'message': message})
    email = EmailMessage(subject, html_message, 'bikoyemmanuel531@gmail.com', list(subscribers))
    email.content_subtype = "html"  # Important pour envoyer l'email en HTML
    email.send()

def send_newsletter_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        send_newsletter(subject, message)
        messages.success(request, 'Newsletter envoyée avec succès !')
        return redirect('admin_dashboard_view')  # Redirection vers un tableau de bord admin
    return render(request, 'siteweb/send_newsletter.html')

def contact_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ContactForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']
                    
                # Logique pour envoyer un email (ou sauvegarder dans la base de données)
                send_mail(
                    subject=f"Message de : {name}",
                    message=f"Subject: {subject}\n\nMessage: {message}",
                    from_email=email,
                    recipient_list=['bikoyemmanuel531@gmail.com'],  # Remplacez par l'email de réception
                    )
                
                messages.success(request, 'Votre message a été envoyé avec succès!')
                return redirect('contact_view')  # Redirection après succès
    
        else:
            messages.error(request, "Vous devez être connecté pour nous contacter.")
            return redirect('login_view')
    else:
        form = ContactForm()
    return render(request, 'siteweb/contact.html', {'form': form})  # Retour au formulaire si GET


def terms_of_service(request):
    return render(request, 'siteweb/terms_of_service.html')

def privacy_policy(request):
    return render(request, 'siteweb/privacy_policy.html')

def developpement_logiciel(request):
    return render(request, 'siteweb/developpement_logiciel.html')

def analyse_donnees(request):
    return render(request, 'siteweb/analyse_donnees.html')

def consultation(request):
    return render(request, 'siteweb/consultation.html')

def marketing_digital(request):
    return render(request, 'siteweb/marketing_digital.html')

def contact(request):
    return render(request, 'siteweb/contact.html')


def assistance(request):
    return render(request, 'siteweb/assistance.html')


def consultation_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ConsultationForm(request.POST)
            if form.is_valid():
                # Récupération des données du formulaire
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                consultation_type = form.cleaned_data['consultation_type']
                message = form.cleaned_data['message']
                
                # Logique pour envoyer un email (ou sauvegarder dans la base de données)
                send_mail(
                    subject=f"Consultation demandée par {name}",
                    message=f"Type de consultation: {consultation_type}\n\nMessage: {message}",
                    from_email=email,  # Utilisation correcte de l'email de l'expéditeur
                    recipient_list=['bikoyemmanuel531@gmail.com'],  # Remplacez par l'email de réception
                )
                
                messages.success(request, 'Votre demande de consultation a été envoyée avec succès!')
                return redirect('consultation_view')
        else:
            # Envoyer un message d'erreur
            messages.error(request, "Vous devez être connecté !")
            return redirect('login_view')

    else:
        form = ConsultationForm()

    return render(request, 'siteweb/consultation.html', {'form': form})
