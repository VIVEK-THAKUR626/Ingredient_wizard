from django.db import models
from django.contrib.auth.models import User

class RecipeList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class SavedRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    image_url = models.URLField(null=True, blank=True)
    recipe_list = models.ForeignKey(RecipeList, on_delete=models.CASCADE, related_name='saved_recipes', null=True, blank=True)

    def __str__(self):
        return self.title
