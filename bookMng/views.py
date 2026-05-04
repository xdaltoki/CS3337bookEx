from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import MainMenu
from .models import Rating
from .models import Comment
from .models import Favorite
from .forms import BookForm
from .forms import RatingForm
from .forms import CommentForm
from django.http import HttpResponseRedirect
from .models import Book
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy



# Create your views here.


def index(request):
    return render(request,
                  'bookMng/index.html',
                  {
                      'item_list': MainMenu.objects.all()
                  })

def postbook(request):
    submitted = False
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.username = request.user
            book.save()
            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request,
                  'bookMng/postbook.html',
                  {
                      'form': form,
                      'item_list': MainMenu.objects.all(),
                      'submitted': submitted
                  })

def displaybooks(request):
    fav_book_ids = set()
    if request.user.is_authenticated:
        fav_book_ids = set(Favorite.objects.filter(user=request.user).values_list('book_id', flat=True))
    search = request.GET.get('q', '')
    books = Book.objects.all()
    if search:
        books = books.filter(name__icontains=search)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/displaybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books,
                      'fav_book_ids': fav_book_ids,
                      'search': search,
                  })


class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self,form):
        form.save()
        return HttpResponseRedirect(self.success_url)

def book_detail(request, book_id):
    book = Book.objects.get(id=book_id)

    book.pic_path = book.picture.url[14:]
    comments = book.comments.all()  # ordered newest-first via Comment.Meta.ordering
    form = CommentForm() if request.user.is_authenticated else None

    return render(request,
                  'bookMng/book_detail.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book': book,
                      'comments': comments,
                      'form': form,
                  })

@login_required
def add_comment(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.book = book
            comment.user = request.user
            comment.save()
    return redirect('book_detail', book_id=book.id)

def mybooks(request):
    books = Book.objects.filter(username=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/mybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books
                  })

def book_delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()

    return render(request,
                  'bookMng/book_delete.html',
                  {
                      'item_list': MainMenu.objects.all(),
                  })

def aboutus(request):
    return render(request,
                  'bookMng/aboutus.html',
                  {
                      'item_list': MainMenu.objects.all()
                  })

@login_required
def rate_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.username == request.user:
        return redirect('displaybooks')

    existing_rating = Rating.objects.filter(book=book, user=request.user).first()

    if request.method == 'POST':
        if existing_rating:
            form = RatingForm(request.POST, instance=existing_rating)
        else:
            form = RatingForm(request.POST)

        if form.is_valid():
            rating = form.save(commit=False)
            rating.book = book
            rating.user = request.user
            rating.save()
            return redirect('displaybooks')
    else:
        if existing_rating:
            form = RatingForm(instance=existing_rating)
        else:
            form = RatingForm()

    return render(
        request,
        'bookMng/rate_book.html',
        {
            'item_list': MainMenu.objects.all(),
            'book': book,
            'form': form,
        }
    )


@login_required
def toggle_favorite(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, book=book)
    if not created:
        fav.delete()  # already favorited → unfavorite it
    return redirect(request.META.get('HTTP_REFERER', 'displaybooks'))


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('book')
    books = []
    for fav in favorites:
        fav.book.pic_path = fav.book.picture.url[14:]
        books.append(fav.book)
    return render(request, 'bookMng/my_favorites.html', {
        'item_list': MainMenu.objects.all(),
        'books': books,
    })