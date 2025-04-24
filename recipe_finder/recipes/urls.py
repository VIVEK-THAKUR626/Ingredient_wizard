from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('save_recipe/', views.save_recipe, name='save_recipe'),
    path('saved_recipes/', views.view_saved_recipes, name='saved_recipes'),
]