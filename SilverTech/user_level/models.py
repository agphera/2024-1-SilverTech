from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'User'


class Useraccuracy(models.Model):
    id = models.OneToOneField(User, models.DO_NOTHING, db_column='id', primary_key=True)
    level = models.CharField(max_length=255, blank=True, null=True)
    correct_num = models.IntegerField(blank=True, null=True)
    total_correct_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'UserAccuracy'


class BasePictureThemes(models.Model):
    theme_id = models.IntegerField(primary_key=True)
    theme_name = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'base_picture_themes'


class BasePictures(models.Model):
    picture_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    url = models.CharField(db_column='URL', max_length=255, blank=True, null=True)  # Field name made lowercase.
    theme_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'base_pictures'
