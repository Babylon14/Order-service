from django.db import models

class Shop(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"
        ordering = ['name']
    
