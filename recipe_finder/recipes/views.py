import requests
from django.shortcuts import render
from django.http import JsonResponse
import certifi
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SavedRecipe
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import urlencode
from .models import RecipeList

@login_required
def delete_list(request, list_id):
    recipe_list = get_object_or_404(RecipeList, id=list_id, user=request.user)
    if request.method == "POST":
        recipe_list.delete()
        messages.success(request, "List deleted successfully.")
    return redirect('manage_lists')  # Change to your actual list page URL name

@login_required
def create_list(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            RecipeList.objects.create(user=request.user, name=name)
            messages.success(request, "List created successfully!")
    return redirect('manage_lists')  # or wherever your lists page is

@login_required
def manage_lists(request):
    if request.method == 'POST':
        # Create new list
        new_list_name = request.POST.get('new_list_name')
        if new_list_name:
            RecipeList.objects.create(user=request.user, name=new_list_name)
            messages.success(request, "✅ List created!")

        # Rename list
        rename_id = request.POST.get('rename_id')
        new_name = request.POST.get('new_name')
        if rename_id and new_name:
            recipe_list = get_object_or_404(RecipeList, id=rename_id, user=request.user)
            recipe_list.name = new_name
            recipe_list.save()
            messages.success(request, "✏️ List renamed!")

        # Delete list
        delete_id = request.POST.get('delete_id')
        if delete_id:
            recipe_list = get_object_or_404(RecipeList, id=delete_id, user=request.user)
            recipe_list.delete()
            messages.success(request, "🗑️ List deleted!")

        return redirect('manage_lists')

    lists = RecipeList.objects.filter(user=request.user).prefetch_related('saved_recipes')
    return render(request, 'manage_lists.html', {'lists': lists})

def about(request):
    return render(request, 'about.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def unsave_recipe(request, pk):
    saved = get_object_or_404(SavedRecipe, pk=pk, user=request.user)
    saved.delete()
    messages.success(request, "Recipe unsaved.")
    return redirect('saved_recipes')  # Adjust if your view name is different

@login_required
def save_recipe(request):
    if request.method == "POST":
        recipe_id = request.POST.get('recipe_id')
        title = request.POST.get('title')
        image_url = request.POST.get('image_url')
        list_id = request.POST.get('list_id')

        recipe_list = None
        if list_id:
            recipe_list = RecipeList.objects.filter(id=list_id, user=request.user).first()

        SavedRecipe.objects.create(
            user=request.user,
            recipe_id=recipe_id,
            title=title,
            image_url=image_url,
            recipe_list=recipe_list  # assuming this field exists in SavedRecipe
        )
        messages.success(request, "✅ Recipe saved to your list!")

        # Preserve search parameters
        ingredients = request.GET.get('ingredients', '')
        diet = request.GET.get('diet', '')
        cuisine = request.GET.get('cuisine', '')

        # Construct redirect URL with query params
        base_url = reverse('recipe_detail', args=[recipe_id])
        query_string = urlencode({
            'ingredients': ingredients,
            'diet': diet,
            'cuisine': cuisine,
        })
        url = f"{base_url}?{query_string}"

        return redirect(url)

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Or any page
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Function to find recipes from an API based on ingredients
def get_recipes(ingredients, diet=None, cuisine=None):
    url = "https://api.spoonacular.com/recipes/complexSearch"
    api_key = "c607aa20a6c54982ae3ea5f13327d1f5"  # Replace with your API key
    params = {
        'includeIngredients': ingredients,
        'number': 20,
        'apiKey': api_key,
    }

    if diet:
        params['diet'] = diet
    if cuisine:
        params['cuisine'] = cuisine

    response = requests.get(url, params=params, verify=certifi.where())
    data = response.json()
    print("API URL:", response.url)
    print("API response:", response.json())
    return data.get('results', [])  # ✅ .get used on response dict, not input


# View to display the home page and handle ingredient input
def index(request):
    recipes = []
    ingredients_raw = ''
    diet = ''
    cuisine = ''
    
    if request.method == "POST":
        if 'login' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully!")
            else:
                messages.error(request, "Invalid login credentials")
        
        elif 'signup' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            else:
                User.objects.create_user(username=username, password=password)
                messages.success(request, "Account created successfully!")
        
        # Redirect to GET-based search after login/signup
        return redirect('index')

    # GET request — handle recipe search
    import json
    ingredients_raw = request.GET.get('ingredients', '')
    ingredients = ''

    try:
        ingredients_list = [tag['value'] for tag in json.loads(ingredients_raw)]
        ingredients = ','.join(ingredients_list)
    except (TypeError, json.JSONDecodeError):
        ingredients = ingredients_raw

    diet = request.GET.get('diet', '')
    cuisine = request.GET.get('cuisine', '')

    # Save search data to session
    request.session['search_data'] = {
            'ingredients': ingredients_raw,
            'diet': diet,
            'cuisine': cuisine
    }

    if ingredients:
        recipes = get_recipes(ingredients, diet, cuisine)

    else:
        # If GET request, try to restore previous search from session
        search_data = request.session.get('search_data')
        if search_data:
            ingredients_raw = search_data.get('ingredients', '')
            diet = search_data.get('diet', '')
            cuisine = search_data.get('cuisine', '')
            try:
                ingredients_list = [tag['value'] for tag in json.loads(ingredients_raw)]
                ingredients = ','.join(ingredients_list)
            except (TypeError, json.JSONDecodeError):
                ingredients = ingredients_raw
            if ingredients:
                recipes = get_recipes(ingredients, diet, cuisine)

    return render(request, 'index.html', {
        'recipes': recipes,
        'ingredients': ingredients_raw,
        'diet': diet,
        'cuisine': cuisine
    })

def recipe_detail(request, recipe_id):
    api_key = 'c607aa20a6c54982ae3ea5f13327d1f5'
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"

    # ✅ Get query parameters for returning back to search
    ingredients = request.GET.get('ingredients', '')
    diet = request.GET.get('diet', '')
    cuisine = request.GET.get('cuisine', '')

    user_lists = []
    if request.user.is_authenticated:
        user_lists = RecipeList.objects.filter(user=request.user)

    try:
        response = requests.get(url, verify=certifi.where())
        data = response.json()
        
        return render(request, 'detail.html', {
            'recipe': data,
            'ingredients': ingredients,
            'diet': diet,
            'cuisine': cuisine,
            'user_lists': user_lists
        })

    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

