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

@login_required
def save_recipe(request):
    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        title = request.POST.get('title')
        image_url = request.POST.get('image_url')

        # Avoid duplicates
        if not SavedRecipe.objects.filter(user=request.user, recipe_id=recipe_id).exists():
            SavedRecipe.objects.create(
                user=request.user,
                recipe_id=recipe_id,
                title=title,
                image_url=image_url
            )
            messages.success(request, "Recipe saved successfully!")
        else:
            messages.info(request, "Recipe already saved.")

    return redirect('index')


@login_required
def view_saved_recipes(request):
    saved = SavedRecipe.objects.filter(user=request.user)
    return render(request, 'saved_recipes.html', {'saved_recipes': saved})

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

        # Handle recipe search
        ingredients = request.POST.get('ingredients')
        print("Ingredients:", ingredients)
        diet = request.POST.get('diet')
        cuisine = request.POST.get('cuisine')

        if ingredients:
            recipes = get_recipes(ingredients, diet, cuisine)

    return render(request, 'index.html', {'recipes': recipes})


def recipe_detail(request, recipe_id):
    api_key = 'c607aa20a6c54982ae3ea5f13327d1f5'
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"
    try:
        response = requests.get(url, verify=certifi.where())  # You can remove verify=False once SSL is trusted
        data = response.json()
        return render(request, 'detail.html', {'recipe': data})
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})
