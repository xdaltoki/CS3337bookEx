from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('postbook', views.postbook, name='postbook'),
    path('displaybooks', views.displaybooks, name='displaybooks'),
    path('book_detail/<int:book_id>', views.book_detail, name='book_detail'),
    path('mybooks', views.mybooks, name='mybooks'),
    path('book_delete/<int:book_id>', views.book_delete, name='book_delete'),
    path('book/<int:book_id>/rate/', views.rate_book, name='rate_book'),
    path('book/<int:book_id>/comment/', views.add_comment, name='add_comment'),
    path('book/<int:book_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites', views.my_favorites, name='my_favorites'),
    path('aboutus', views.aboutus, name='aboutus'),
]