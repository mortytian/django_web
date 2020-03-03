# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Account(models.Model):
    id = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'account'


class Allfreq(models.Model):
    word = models.TextField(blank=True, null=True)
    freqcet4 = models.IntegerField(blank=True, null=True)
    freqcet6 = models.IntegerField(blank=True, null=True)
    freqz4 = models.IntegerField(blank=True, null=True)
    freqz8 = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allFreq'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Books(models.Model):
    bookid = models.CharField(max_length=20, blank=True, null=True)
    bookname = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'books'


class Coca(models.Model):
    rank = models.TextField(db_column='RANK', blank=True, null=True)  # Field name made lowercase.
    pos = models.TextField(db_column='PoS', blank=True, null=True)  # Field name made lowercase.
    word = models.TextField(blank=True, null=True)
    total = models.BigIntegerField(db_column='TOTAL', blank=True, null=True)  # Field name made lowercase.
    spoken = models.IntegerField(db_column='SPOKEN', blank=True, null=True)  # Field name made lowercase.
    fiction = models.BigIntegerField(db_column='FICTION', blank=True, null=True)  # Field name made lowercase.
    magazine = models.BigIntegerField(db_column='MAGAZINE', blank=True, null=True)  # Field name made lowercase.
    newspaper = models.IntegerField(db_column='NEWSPAPER', blank=True, null=True)  # Field name made lowercase.
    academic = models.IntegerField(db_column='ACADEMIC', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'coca'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Four(models.Model):
    word = models.TextField(blank=True, null=True)
    trans = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'four'


class Proeight(models.Model):
    word = models.TextField(blank=True, null=True)
    trans = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proeight'


class Profour(models.Model):
    word = models.TextField(blank=True, null=True)
    trans = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profour'


class Six(models.Model):
    word = models.TextField(blank=True, null=True)
    trans = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'six'




class UserWordsInfomation(models.Model):
    user_id = models.CharField(max_length=45, blank=True, null=True)
    book_id = models.CharField(max_length=45, blank=True, null=True)
    word = models.TextField(blank=True, null=True)
    learn_time = models.CharField(max_length=40, blank=True, null=True)
    review_time = models.TextField(blank=True, null=True)  # This field type is a guess.
    unknown_time = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'user_words_infomation'

class UserSetting(models.Model):
    user_id = models.CharField(max_length=45, blank=True, null=True)
    learn_num = models.IntegerField(blank=True, null=True)
    review_num = models.IntegerField(blank=True, null=True)
    total_words = models.IntegerField(blank=True, null=True)
    learned_num = models.IntegerField(blank=True, null=True)

class user_words_content(models.Model):
    user_id = models.CharField(max_length=45, blank=True, null=True)
    book_id = models.CharField(max_length=45, blank=True, null=True)
    word = models.TextField(blank=True, null=True)
    part_of_speech = models.TextField(blank=True, null=True)
    chinese = models.TextField(blank=True, null=True)
    sentence = models.TextField(blank=True, null=True)  # This field type is a guess.