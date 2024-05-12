from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'User'


class UserAccuracy(models.Model):
    user_id = models.AutoField(primary_key=True)
    successive_correct = models.IntegerField()
    successive_wrong = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'UserAccuracy'

        

class UserProceeding(models.Model):
    user = models.OneToOneField(User, models.DO_NOTHING, primary_key=True)
    level = models.IntegerField()
    last_order = models.IntegerField()
    is_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'UserProceeding'


class BasePictureThemes(models.Model):
    theme_id = models.IntegerField(primary_key=True)
    theme_name = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'base_picture_themes'


class BasePictures(models.Model):
    picture_id = models.IntegerField(primary_key=True)
    theme_id = models.IntegerField()
    title = models.CharField(max_length=20, blank=True, null=True)
    url = models.CharField(db_column='URL', max_length=255, blank=True, null=True)  # Field name made lowercase.
    level = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'base_pictures'