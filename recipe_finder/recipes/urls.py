from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('save_recipe/', views.save_recipe, name='save_recipe'),
    path('about/', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('lists/', views.manage_lists, name='manage_lists'),
    path('create-list/', views.create_list, name='create_list'),
    path('delete-list/<int:list_id>/', views.delete_list, name='delete_list'),
    path('remove-recipe/<int:recipe_id>/', views.remove_saved_recipe, name='remove_saved_recipe'),

]