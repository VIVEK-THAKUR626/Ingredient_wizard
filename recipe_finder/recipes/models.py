from django.db import models
from django.contrib.auth.models import User

class SavedRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.IntegerField()
    title = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


# Create your models here.
