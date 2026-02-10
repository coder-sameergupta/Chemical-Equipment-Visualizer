from django.db import models

class UploadHistory(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads/')
    total_records = models.IntegerField(default=0)

    def __str__(self):
        return f"Upload {self.id} at {self.uploaded_at}"

class EquipmentData(models.Model):
    upload = models.ForeignKey(UploadHistory, on_delete=models.CASCADE, related_name='equipment')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=255)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()

    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"
