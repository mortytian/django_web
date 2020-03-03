from django.views.generic import View
from django.shortcuts import render,redirect,reverse
from .models import Account,UserSetting,user_words_content,UserSetting
from .tools import get_study_words,generateWord,calculateLevel,processtxt,add_words_content
import json
import mysql.connector as sqldb
import random
import os
import datetime

class MainPage(View):
    TEMPLATES = 'MainPage.html'

    def get(self, request):
        data = {}
        if 'userid' in request.session.keys():
            data['login'] = True
        return render(request, self.TEMPLATES, data)


class Register(View):
    TEMPLATES = 'Register.html'

    def get(self, request):
        data = {}
        return render(request, self.TEMPLATES, data)


    def post(self, request):
        data = {}
        # 获取表单信息
        username = request.POST.get('username')
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        checkpassword = request.POST.get('checkpassword')
        print(username)
        print(userid)
        print(password)
        print(checkpassword)

        # 对信息进行验证

        # 检查是否有字段为空
        if not (username and userid and password and checkpassword):
            error = '字段不能为空'
            data['error'] = error
            return render(request, self.TEMPLATES, data)

        # 检查账号长度是否超过20大于6
        if len(userid) > 20 or len(userid) < 6:
            error = '账号长度不符合规定'
            data['error'] = error
            return render(request, self.TEMPLATES, data)

        # 检查账号是否重复
        user = Account.objects.filter(id=userid).exists()
        if user:
            error = '账号重复'
            data['error'] = error
            return render(request, self.TEMPLATES, data)

        # 检查password与checkpassword是否一只
        if password != checkpassword:
            print(password)
            print(checkpassword)
            error = '两次输入密码不一致'
            data['error'] = error
            return render(request, self.TEMPLATES, data)

        # 检查password长度是否符合规定
        if len(password) > 20 or len(password) < 6:
            error = '密码长度不符合规定'
            data['error'] = error
            return render(request, self.TEMPLATES, data)
        Account.objects.create(id=userid, name=username, password=password)
        UserSetting.objects.create(user_id=userid,learn_num=20,review_num=20,total_words=2755,learned_num=0)
        self.insert_data(userid)

        return redirect(reverse('Login'))

    def insert_data(self,userid):
        file = "./static/datas/cet-4.txt"
        resultCET4 = processtxt(file)
        words = resultCET4
        words = words[0:200]
        print('123')
        add_words_content(userid, "0001", words)
        print(words)

class Login(View):
    TEMPLATES = 'Login.html'

    def get(self, request):
        data = {}
        return render(request, self.TEMPLATES, data)


    def post(self, request):
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        if not(userid and password):
            error = '账号或密码不可为空'
            data = {}
            data['error'] = error
            return render(request, self.TEMPLATES, data)
        user = Account.objects.filter(id=userid, password=password).all().first()

        if not user:
            error = '账号或密码错误'
            data = {}
            data['error'] = error
            return render(request, self.TEMPLATES, data)

        request.session['userid'] = userid
        request.session['username'] = user.name
        return redirect(reverse('wordsweb_study'))




class wordsweb_study(View):
    TEMPLATES = 'wordsweb_study.html'

    def get(self, request):
        data = {}
        if 'finish' not in request.session.keys() or request.session['finish'] == False:
            print(request.session.keys())
            username = request.session['username']
            user_id = request.session['userid']
            setting = UserSetting.objects.filter(user_id=user_id).first()
            learn_num = setting.learn_num
            review_num = setting.review_num
            total_words = setting.total_words
            learned_num = setting.learned_num
            print(request.session.keys())
            percent = round(learned_num/total_words,5)
            days = (total_words - learned_num)/ learn_num
            finish_day =(datetime.datetime.now()+datetime.timedelta(days=days)).strftime("%Y年%m月%d日")
            data['username'] = username
            data['finish'] = False
            data['learn_num'] = learn_num
            data['review_num'] = review_num
            data['total_words'] = total_words
            data['not_learn'] = review_num + learn_num
            data['total_words'] = total_words
            data['learned_num'] = learned_num
            data['percent'] = percent
            data['finish_day'] = finish_day

            return render(request, self.TEMPLATES, data)
        else:
            username = request.session['username']
            data['username'] = username
            data['finish'] = request.session['finish']
            return render(request, self.TEMPLATES, data)




class wordsweb_memory(View):
    TEMPLATES = 'wordsweb_memory.html'

    def get(self,request):
        data = {}
        username = request.session['username']
        data['username'] = username
        userid = request.session['userid']
        setting = UserSetting.objects.get(user_id=userid)
        learned_num = setting.learned_num
        learn_num = setting.learn_num
        review_num = setting.review_num
        words = user_words_content.objects.all()[learned_num:learned_num+learn_num+review_num]
        mywords = {}
        for word in words:
            mywords[word.word] = [{'part_of_speech': word.part_of_speech,
                                  'chinese' : word.chinese,
                                   'sentence' : json.loads(word.sentence)}]

        words = json.dumps(mywords,ensure_ascii=False)
        data['words'] = words
        return render(request, self.TEMPLATES, data)

    def post(self,request):
        userid =request.session['userid']
        setting = UserSetting.objects.get(user_id=userid)
        setting.learned_num += setting.learn_num
        setting.save()
        # request.session['finish'] = True
        return redirect(reverse('wordsweb_study'))


class Setting(View):
    TEMPLATES = 'Setting.html'

    def get(self, request):
        userid = request.session['userid']
        data = self.get_data(userid)
        username = request.session['username']
        data['username'] = username
        return render(request, self.TEMPLATES, data)

    def post(self,request):
        new_name = request.POST.get('new_name')
        learn_num = request.POST.get('learn_num')
        review_num = request.POST.get('review_num')
        user_id = request.session['userid']
        UserSetting.objects.filter(user_id=user_id).update(learn_num=learn_num,review_num=review_num)
        Account.objects.filter(id=user_id).update(name=new_name)
        request.session['username'] = new_name


        return redirect(reverse('wordsweb_study'))

    def get_data(self, user_id):
        setting = UserSetting.objects.filter(user_id=user_id).first()
        learn_num = setting.learn_num
        review_num = setting.review_num
        learn = [5,10,15,20,25,30,40,50,60,70,90,100,120,140,160,180,200]
        review = [20,25,30,35,40,45,50,60,70,90,100,120,140,160,180,200]

        learn_selection = []
        review_selection = []
        for l in learn:
            if l != learn_num:
                learn_selection.append('<option value="{}">{}</option>'.format(l,l))
            else:
                learn_selection.append('<option value="{}" selected>{}</option>'.format(l, l))

        for r in review:
            if r != review_num:
                review_selection.append('<option value="{}">{}</option>'.format(r,r))
            else:
                review_selection.append('<option value="{}" selected>{}</option>'.format(r, r))
        data = {}
        data['learn_selection'] = ''.join(learn_selection)
        data['review_selection'] = ''.join(review_selection)
        return data

class TestVocabulary(View):
    TEMPLATES = 'testVocabulary.html'

    def get(self,request):
        words = generateWord()
        words = json.loads(words)
        level1 = words['level1']
        level2 = words['level2']
        level3 = words['level3']
        level4 = words['level4']
        level5 = words['level5']
        level6 = words['level6']
        level1_html = []
        level2_html = []
        level3_html = []
        level4_html = []
        level5_html = []
        level6_html = []
        for word in level1:
            word = word.strip()
            level1_html.append('<div class="col s3"><input type = "checkbox" class ="filled-in col s1 " id="{}" name="{}" value="{}" /> <label for ="{}"> {} </label ></div> '.format(word,'level1',word,word,word))
        for word in level2:
            word = word.strip()
            level2_html.append('<div class="col s3"><input type = "checkbox" class ="filled-in col s1 " id="{}" name="{}" value="{}" /> <label for ="{}"> {} </label ></div> '.format(word,'level2',word,word,word))
        for word in level3:
            word = word.strip()
            level3_html.append('<div class="col s3"><input type = "checkbox" class ="filled-in col s1 " id="{}" name="{}" value="{}" /> <label for ="{}"> {} </label ></div> '.format(word,'level3',word,word,word))
        for word in level4:
            word = word.strip()
            level4_html.append('<div class="col s3"><input type = "checkbox" class ="filled-in col s1 " id="{}" name="{}" value="{}" /> <label for ="{}"> {} </label ></div> '.format(word,'level4',word,word,word))
        for word in level5:
            word = word.strip()
            level5_html.append('<div class="col s3"><input type = "checkbox" class ="filled-in col s1 " id="{}" name="{}" value="{}" /> <label for ="{}"> {} </label ></div> '.format(word,'level5',word,word,word))
        for word in level6:
            word = word.strip()
            level6_html.append('<div class="col s3"><input type = "checkbox" class ="filled-in col s1 " id="{}" name="{}" value="{}" /> <label for ="{}"> {} </label ></div> '.format(word,'level6',word,word,word))
        page_html = ''
        page_html += "".join(level1_html)
        page_html += "".join(level2_html)
        page_html += "".join(level3_html)
        page_html += "".join(level4_html)
        page_html += "".join(level5_html)
        page_html += "".join(level6_html)

        data = {}
        data['page_html']  = page_html
        username = request.session['username']
        data['username'] = username

        return render(request, self.TEMPLATES, data)

    def post(self, request):
        l1 = request.POST.getlist('level1')
        l2 = request.POST.getlist('level2')
        l3 = request.POST.getlist('level3')
        l4 = request.POST.getlist('level4')
        l5 = request.POST.getlist('level5')
        l6 = request.POST.getlist('level6')
        # {"level1": 5, "level2": 5, "level3": 5, "level4": 5, "level5": 5, "level6": 5}
        number = {"level1": None, "level2": None, "level3": None, "level4": None, "level5": None, "level6": None}
        number['level1'] = len(l1)
        number['level2'] = len(l2)
        number['level3'] = len(l3)
        number['level4'] = len(l4)
        number['level5'] = len(l5)
        number['level6'] = len(l6)

        result = json.dumps(number)
        result = calculateLevel(result)
        print(result)
        data = {}

        request.session['Vocabularynum']  = result
        return redirect(reverse('ShowVocabularyNum'))

class ShowVocabularyNum(View):
    TEMPLATES = 'ShowVocabularyNum.html'

    def get(self, request):
        data = {}
        Vocabularynum = request.session['Vocabularynum']
        data['Vocabularynum'] = Vocabularynum
        username = request.session['username']
        data['username'] = username
        return render(request, self.TEMPLATES, data)




class test(View):
    TEMPLATES = 'test.html'

    def get(self, request):
        data = {}
        datalist = [123,321,1,2,3,4,5,6,7]
        dl = json.dumps(datalist)
        data['test'] = dl
        return render(request, self.TEMPLATES, data)

    def post(self,request):
        data = {}
        datalist = [123,321,1,2,3,4,5,6,7]
        dl = json.dumps(datalist)
        print(request.POST.get('t'))
        data['test'] = dl
        return render(request, self.TEMPLATES, data)

