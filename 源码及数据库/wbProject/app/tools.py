#encoding:utf-8
import mysql.connector as sqldb
import re
import  time
import json
import math
import requests
import re
import  ast
import random


def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True

    return False

def is_digit(string):
    for ch in string:
        if '0'<=ch<='9':
            return True


    return False


def processtxt(filename):
    resultlist=[]
    f=open(filename,encoding='utf-8')
    for line in f.readlines():
        line=line.replace("\n","").replace(">","")

        parts=line.split("|")
        if len(parts[0])==1:
            continue
        if is_chinese(parts[1]) or is_chinese(parts[2]) or is_digit(parts[1]) or is_digit(parts[2]):
            continue

        parts[2] = [parts[2]]
        resultlist.append((parts[0],parts[1],parts[3],parts[2]))

    print(len(resultlist))
    f.close()

    return resultlist

def add_words_content(user_id, book_id, words):

    conn = sqldb.connect(
        user='calmwalter',
        password='xu123456',
        database='wordking',
        host='cdb-hqoaiyi4.bj.tencentcdb.com',
        port='10208'
    )
    cursor = conn.cursor()
    for word in words:
        print(word)
        cursor.execute(
            'insert into wordking.app_user_words_content(user_id, book_id, word,part_of_speech, chinese, sentence) ' +
            'values(\"'+user_id+'\",\"'+book_id+'\",\"' +
            word[0]+'\",\"'+word[1]+'\",\"'+word[2]+'\",\'["'+word[3][0].replace('"','\\\'')+'"]\');'
        )
        conn.commit()
    cursor.close()

def get_words_information(user_id, book_id):
    conn = sqldb.connect(
        user='calmwalter',
        password='xu123456',
        database='wordking',
        host='cdb-hqoaiyi4.bj.tencentcdb.com',
        port='10208'
    )
    cursor = conn.cursor()
    cursor.execute(
        'select concat(\'{"\',group_concat(word,\'":[\',concat(\'{"learn_time":\',ifnull(learn_time,\'\"\"\'),\',"review_time":\',ifnull(review_time,"[]"),\',"unknown_time":\',ifnull(unknown_time,"[]"),\'}\'),\']\'),\'}\') as words_infomation '+
        'from user_words_infomation '+
        'where user_id = "'+user_id+'" and book_id="'+book_id+'";')
    words_infomation = cursor.fetchall()
    cursor.close()
    if words_infomation:
        return words_infomation[0][0].decode('utf-8')
        # return json.dumps(words_infomation[0][0])
    else:
        return None


def get_words_content(user_id, book_id):
    conn = sqldb.connect(
        user='calmwalter',
        password='xu123456',
        database='wordking',
        host='cdb-hqoaiyi4.bj.tencentcdb.com',
        port='10208'
    )
    cursor = conn.cursor()
    cursor.execute(
        'select concat(\'{"\',group_concat(word,\'":[\',concat(\'{"part_of_speech":"\', part_of_speech,\'","chinese":"\',chinese,\'","sentence":\',sentence,\'}\'),\']\'),\'}\') as words_content '+
        'from user_words_content '+
        'where user_id = "'+user_id+'" and book_id="'+book_id+'";')
    words_content = cursor.fetchall()
    cursor.close()
    if words_content:
        return words_content[0][0].decode('utf-8')
    else:
        return None


'''
艾宾浩斯
1:第一天
2：第二天
3：第四天
4：第七天
5：第十五天
一共出现五次review，!!!第一次看见他就算一次review!!!
也就是review对应的value，list中最多有五个值，达到五个就不让他再复习，表示用户背完了
如果用户点了忘记就把这个单词的三个属性全部置空
'''


def get_study_words(words_information, words_content, recite_amount, review_amount,today):
    ReturnunLearnDict={}
    ReturnReviewDict={}

    #words_information=json.loads(words_information)
    UnLearnDict={}
    LearnedDict={}




    '''
    分割已学和未学
    '''

    for item in words_information:
        if words_information[item][0]['learn_time'] is not  None and words_information[item][0]['review_time'] is not None and len(words_information[item][0]['review_time'])<=4 :
            LearnedDict[item]=words_information[item][0]
        elif  words_information[item][0]['learn_time'] is  None:
            UnLearnDict[item]=words_information[item][0]

    #print(UnLearnDict)
    #print(LearnedDict)

    ReciteKey=list(UnLearnDict.keys())#返回给定数量的未学
    for i in range (recite_amount):
        if i+1 <=len(UnLearnDict) :
            ReturnunLearnDict[ReciteKey[i]]=UnLearnDict[ReciteKey[i]]

    # print(ReturnunLearnDict)



    '''
    先排序已学
    然后返回一定数量的已学
    1.得到每个单词下一次复习时间戳
    2.返回复习时间戳与当前时间戳相同的单词，此为第二优先级
    3.如果需要复习的单词超过限额，怎么做到下一次先把这些搞出来？
    4.复习时间戳小于当前时间戳的单词为第一优先级
      一共只考虑以上两个优先级
    '''

    tempdict={}
    for item in LearnedDict:
        #print(LearnedDict[item]['review_time'][len(LearnedDict[item]['review_time'])-1])
        tempdict[item]={}
        tempdict[item]['review_time']=LearnedDict[item]['review_time'][len(LearnedDict[item]['review_time'])-1]
        tempdict[item]['number']=len(LearnedDict[item]['review_time'])
    # print(tempdict)

    review_time_table={
        '1':24*3600*1,
        '2':24*3600*2,
        '3':24*3600*3,
        '4':24*3600*8

    }
    for item in tempdict:
        tempdict[item]['review_time']=tempdict[item]['review_time']+review_time_table[str(tempdict[item]['number'])]
    # print(tempdict)



    keylist=sorted(tempdict, key=lambda k: tempdict[k]['review_time'])
    tempdict2={}
    for item in keylist:
        tempdict2[item]=tempdict[item]
    # print(tempdict2)


    ReturnReviewList=[]

    for item in tempdict:
        if tempdict[item]['review_time']<today:
            ReturnReviewList.append(item)
        elif tempdict[item]['review_time']==today:
            ReturnReviewList.append(item)

    ReturnReviewList=ReturnReviewList[0:review_amount]

    FinalDict={'learn':[],'review':[]}
    FinalDict2={}
    gogogodict={}

    for item in ReturnunLearnDict:
        print(item)
        print(type(item))
        gogogodict={}
        gogogodict[item]=words_content[item]
        FinalDict['learn'].append(gogogodict)
        FinalDict2[item]=words_content[item]
    for item in ReturnReviewList:
        gogogodict={}
        gogogodict[item]=words_content[item]
        FinalDict['review'].append(gogogodict)
        FinalDict2[item]=words_content[item]

    # print(FinalDict)
    return json.dumps(FinalDict,ensure_ascii=False),json.dumps(FinalDict2,ensure_ascii=False)



import pymysql
import json
import random as ran
'''
调用generateword（），返回一个json，包含六个等级，每个等级20个单词
{
    "level1": ["five", "light", "several", "after", "fall", "perhaps", "during", "person", "up", "leave"],
    ...
    ...
    "level6": ["five", "light", "several", "after", "fall", "perhaps", "during", "person", "up", "leave"]
}

用户点击表示认识

调用calculatelevel（），传入一个json，分别是六个等级里认识的单词数目.......返回值str是单词量
{
    "level1": 5,
    "level2": 5,
    "level3": 5,
    "level4": 5,
    "level5": 5,
    "level6": 5
}
'''
def getRandomData(number,data:list):
    ran.shuffle(data)
    result=list()
    for i in range(number):
        result.append(data[i])
    return result;


def DBquery(start,end):
    total=list()

    conn = pymysql.connect(host="cdb-hqoaiyi4.bj.tencentcdb.com", user="Geralt",password="ping123456",database="wordking",charset="utf8",port=10208)
    cursor=conn.cursor()

    sql1 = "select word from coca where TOTAL>= {} and TOTAL <= {} ".format(start,end)
    #改成正數
    cursor.execute(sql1)

    result=cursor.fetchall()

    #print(len(result))
    for item in result:
        total.append(item[0])
    #for item in total:
    #    print(item)

    conn.commit()
    cursor.close()
    conn.close()

    if  len(total)==0:
        print('No result find in DB')

    return total

def generateWord():#返回六个等级的词汇,来自于coca
    result={}
    for i in range(6):
        temp=i+1
        result.update({"level"+str(temp):[]})
#level1
    fres1=89232
    free1=300000

    result1=DBquery(fres1,free1)
#level2
    fres2=10002
    free2=89232

    result2=DBquery(fres2,free2)
#level3
    fres3=1828
    free3=10002

    result3=DBquery(fres3,free3)
#level4
    fres4=1148
    free4=1828

    result4=DBquery(fres4,free4)
#level5
    fres5=488
    free5=1148

    result5=DBquery(fres5,free5)
#level6
    fres6=0
    free6=488

    result6=DBquery(fres6,free6)


    for item in getRandomData(10,result1):
        result['level1'].append(item)

    for item in getRandomData(10,result2):
        result['level2'].append(item)

    for item in getRandomData(25,result3):
        result['level3'].append(item)

    for item in getRandomData(25,result4):
        result['level4'].append(item)

    for item in getRandomData(10,result5):
        result['level5'].append(item)

    for item in getRandomData(10,result6):
        result['level6'].append(item)


    jsoninfo = json.dumps(result)


    return jsoninfo

def calculateLevel(result):
    '''這個算法還是有點問題'''

    result=json.loads(result)
    #totallist=[500,3448-500,10000-3448,3000,7000,40024]
    totallist=[500,4000,6000,8000,12000]
    samplelist=[10,10,25,25,10,10]

    limitlist=[]
    '''暂时不考虑limit，不考虑这人乱填的情况'''
    ratelist=list()


    for i in range(5):
        temp=i+1
        ratelist.append(result['level'+str(temp)]/samplelist[i])
    # for item in ratelist:
    #     print(item)

    final=0

    for i in range(5):

        temp=totallist[i]*ratelist[i]
        final+=int(temp)
    # print(str(int(final/2)))

    '''第六个level作为加分项，不计入总单词评估'''


    return str(int(final/2))




if __name__=="__main__":
    words_information ={
    'word0' : [
                {
                    'learn_time': None ,
                    'review_time':  None,
                    'unknown_time':None
                }
             ],

    'word2' :[{
                    'learn_time'  : 123456,
                    'review_time' : [321654,654654],
                    'unknown_time' : [987,987,987]
        }
            ],
    'word3' : [
                {
                    'learn_time': None ,
                    'review_time':  None,
                    'unknown_time':None
                }
             ],
    'word4' : [
                {
                    'learn_time': 23,
                    'review_time':  [12],
                    'unknown_time':[33]
                }
             ],

    'word5' : [
                {
                    'learn_time': 222,
                    'review_time':  [12,99,654654],
                    'unknown_time':[33]
                }
             ],

    }

    words_content ={
        'abandon' : [
            {
                            'part_of_speech' : 'v'  ,
                            'chinese' : '丢弃；放弃，抛弃',
                            'sentence' : ['The baby had been abandoned by its mother.',
                                            'The study showed a deep fear among the elderly of being abandoned to the care of strangers.'
                                        ]
            },

            {
                            'part_of_speech' : 'adj',
                            'chinese' : '哈哈哈哈哈',
                            'sentence' : ['xxxx']
            }



                    ],
            'word0' : [
            {
                            'part_of_speech' : 'v'  ,
                            'chinese' : '丢',
                            'sentence' : ['The baby had been abandoned by its mother.']
            },  ],

                'word1' : [
            {
                            'part_of_speech' : 'v'  ,
                            'chinese' : 'asdadg',
                            'sentence' : ['The baby had been abandoned by its mother.']
            },  ],

                'word2' : [
            {
                            'part_of_speech' : 'v'  ,
                            'chinese' : 'agfgdg',
                            'sentence' : ['The baby had been abandoned by its mother.']
            },  ],

                'word3' : [
            {
                            'part_of_speech' : 'v'  ,
                            'chinese' : 'asdgzdg',
                            'sentence' : ['The baby had been abandoned by its mother.']
            },  ],

                'word4' : [
            {
                            'part_of_speech' : 'v'  ,
                            'chinese' : 'atfhyetyg',
                            'sentence' : ['The baby had been abandoned by its mother.']
            },  ],

                'word5' : [
            {
                            'part_of_speech' : 'v'  ,
                            'chinese' : 'a5464655g',
                            'sentence' : ['The baby had been abandoned by its mother.']
            },  ]

    }
    '''
    for item in words_content:
        for itemx in words_content[item]:
            print(itemx)
    '''

    get_study_words(words_information,words_content,10,10,0)


'''
一小时:3600
一天:3600*24
'''
today=0
def calculate_finish_day(total_word, recite_amount, review_amount, words_information, start_time=today):

    #words_information=json.loads(words_information)
    UnLearnDict={}
    LearnedDict={}

    for item in words_information:
        if words_information[item][0]['learn_time'] is not  None and words_information[item][0]['review_time'] is not None and len(words_information[item][0]['review_time'])<=4:
            LearnedDict[item]=words_information[item][0]
        elif words_information[item][0]['learn_time'] is   None:
            UnLearnDict[item]=words_information[item][0]
    # print(UnLearnDict)
    # print(LearnedDict)

    RemainLearnDay=0
    RemainLearnDay=math.ceil(len(UnLearnDict)/recite_amount)*3600*24*15

    '''
    剩余复习时间
    先做一个排序，返回单词和对应的最晚复习时间，和第几次复习
    用最晚复习时间计算结束时间，然后降序排，得到最终list，该list中第一个就是最晚复习完的单词
    '''
    tempdict={}
    for item in LearnedDict:
        #print(item)
        #print(LearnedDict[item]['review_time'][len(LearnedDict[item]['review_time'])-1])
        tempdict[item]={}
        tempdict[item]['review_time']=LearnedDict[item]['review_time'][len(LearnedDict[item]['review_time'])-1]
        tempdict[item]['number']=len(LearnedDict[item]['review_time'])
    # print(tempdict)

    review_time_table={
        '1':24*3600*1+24*3600*2+24*3600*3+24*3600*8,
        '2':24*3600*2+24*3600*3+24*3600*8,
        '3':24*3600*3+24*3600*8,
        '4':24*3600*8

    }
    for item in tempdict:
        tempdict[item]['review_time']=tempdict[item]['review_time']+review_time_table[str(tempdict[item]['number'])]
    # print(tempdict)



    keylist=sorted(tempdict, key=lambda k: tempdict[k]['review_time'],reverse=True)
    tempdict2={}
    for item in keylist:
        tempdict2[item]=tempdict[item]
#     # print(tempdict2)


    RemainReviewDay=0
    RemainReviewDay=tempdict2[list(tempdict2.keys())[0]]['review_time']
    RemainReviewDay=RemainReviewDay+3600*24*math.ceil(len(tempdict2.keys())/review_amount) #计算一下当前剩下的复习单词要分成几天，估算一下，不精确

    RemainLearnDay=start_time+RemainLearnDay


#     # print(RemainLearnDay)
    # print(RemainReviewDay)



    if RemainLearnDay>RemainReviewDay:
        return str(RemainLearnDay)


    return str(RemainReviewDay)



if __name__ == "__main__":
    words_information = {
        'word0': [
            {
                'learn_time': None,
                'review_time': None,
                'unknown_time': None
            }
        ],

        'word2': [{
            'learn_time': 123456,
            'review_time': [321654, 654654],
            'unknown_time': [987, 987, 987]
        }
        ],
        'word3': [
            {
                'learn_time': None,
                'review_time': None,
                'unknown_time': None
            }
        ],
        'word4': [
            {
                'learn_time': 23,
                'review_time': [12],
                'unknown_time': [33]
            }
        ],

        'word5': [
            {
                'learn_time': 222,
                'review_time': [12, 99, 654654],
                'unknown_time': [33]
            }
        ],

    }

    words_content = {
        'abandon': [
            {
                'part_of_speech': 'v',
                'chinese': '丢弃；放弃，抛弃',
                'sentence': ['The baby had been abandoned by its mother.',
                             'The study showed a deep fear among the elderly of being abandoned to the care of strangers.'
                             ]
            },

            {
                'part_of_speech': 'adj',
                'chinese': '哈哈哈哈哈',
                'sentence': ['xxxx']
            }

        ],
        'word0': [
            {
                'part_of_speech': 'v',
                'chinese': '丢',
                'sentence': ['The baby had been abandoned by its mother.']
            }, ],

        'word1': [
            {
                'part_of_speech': 'v',
                'chinese': 'asdadg',
                'sentence': ['The baby had been abandoned by its mother.']
            }, ],

        'word2': [
            {
                'part_of_speech': 'v',
                'chinese': 'agfgdg',
                'sentence': ['The baby had been abandoned by its mother.']
            }, ],

        'word3': [
            {
                'part_of_speech': 'v',
                'chinese': 'asdgzdg',
                'sentence': ['The baby had been abandoned by its mother.']
            }, ],

        'word4': [
            {
                'part_of_speech': 'v',
                'chinese': 'atfhyetyg',
                'sentence': ['The baby had been abandoned by its mother.']
            }, ],

        'word5': [
            {
                'part_of_speech': 'v',
                'chinese': 'a5464655g',
                'sentence': ['The baby had been abandoned by its mother.']
            }, ]

    }

    '''
    for item in words_content:
        for itemx in words_content[item]:
            print(itemx)
    '''

    # information = get_words_information('123','1234')
    content = get_words_content('12306','12345')
    # information = json.loads(information)
    # print(content)
    # content = json.loads(content)

    print(content)
    # print(information)
    # a,b = get_study_words(information,content,10,10,0)
    # print(a)
    # print(b)
    # conn = sqldb.connect(
    #     user='calmwalter',
    #     password='xu123456',
    #     database='wordking',
    #     host='cdb-hqoaiyi4.bj.tencentcdb.com',
    #     port='10208'
    # )
    # cursor = conn.cursor()
    # cursor.execute('select * from four limit 10;')
    # words_infomation = cursor.fetchall()
    # cursor.close()
    # print(words_infomation)
    # print(type(generateWord()))