import requests
from django.shortcuts import render
from django.http import JsonResponse

# Function to find recipes from an API based on ingredients
def get_recipes(ingredients):
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    api_key = "c607aa20a6c54982ae3ea5f13327d1f5"  # Replace with your API key
    params = {
        'ingredients': ingredients,
        'number': 5,  # Limit to 5 recipes
        'apiKey': api_key
    }
    response = requests.get(url, params=params)
    return response.json()

# View to display the home page and handle ingredient input
def index(request):
    recipes = []
    if request.method == "POST":
        ingredients = request.POST.get('ingredients')
        if ingredients:
            recipes = get_recipes(ingredients)
    return render(request, 'index.html', {'recipes': recipes})

def recipe_detail(request, recipe_id):
    api_key = 'your_spoonacular_api_key'
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"
    try:
        response = requests.get(url, verify=False)  # You can remove verify=False once SSL is trusted
        data = response.json()
        return render(request, 'detail.html', {'recipe': data})
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})