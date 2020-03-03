from django.urls import path
from .views import MainPage,Register,Login,wordsweb_study,test,wordsweb_memory,Setting,TestVocabulary,ShowVocabularyNum

urlpatterns = [
    path('wordking', MainPage.as_view(), name='MainPage'),
    path('register', Register.as_view(), name='Register'),
    path('login', Login.as_view(), name = 'Login'),
    path('wordsweb/study', wordsweb_study.as_view(), name='wordsweb_study'),
    path('wordsweb/memory', wordsweb_memory.as_view(), name='wordsweb_memory'),
    path('wordsweb/setting', Setting.as_view(), name='Setting'),
    path('wordsweb/testvocabulary', TestVocabulary.as_view(), name='TestVocabulary'),
    path('wordsweb/ShowVocabularyNum', ShowVocabularyNum.as_view(), name='ShowVocabularyNum'),

    path('test', test.as_view(), name='test')
]