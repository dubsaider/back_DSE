from django.db import models

class JsonFile(models.Model):
    file = models.FileField(upload_to='json_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name