# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 13:09:21 2020

@author: user
"""
# gevent
from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer
# gevent end

from flask import Flask, request, jsonify, render_template, copy_current_request_context, send_from_directory
from flask.ctx import _request_ctx_stack
from flask_pymongo import PyMongo
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy as np
import werkzeug
import json
import time
import os
import re
import csv
import threading
import gridfs
import codecs, sys
import plotly
import plotly.offline as py                    #保存图表，相当于plotly.plotly as py，同时增加了离线功能
from plotly.graph_objs import Scatter, Layout              #创建各类图表
import plotly.figure_factory as ff  
import plotly.graph_objs as go
from flask import url_for


app = Flask(__name__, static_folder='./watch-data-table-master/build', static_url_path="/")
app.config['Debug'] = True
app.config["MONGO_URI"] = "mongodb://Hua:Wahahaha443@127.0.0.1:27017/newscons?authSource=admin"

mongo = PyMongo(app)
Key = ['Notification', 'Sensor', "Telephony", 'AppUsage', 'Battery', 'Connectivity', 'Ringer', 'ActivityRecognition', 'TransportationMode', "myAccessibility", "AppTimes", 'QuestionnaireAns', "ScreenShotDecider"]
UserKey = ["device_id", "todayMCount", "todayNCount", "allMCount", "allNCount", "total"]
SearchKey = ["id", "DayNumber", "todayMCount", "todayNCount", "totalMCount", "totalNCount", "total", "startDay", "endDay"]
IsAliveKey = ["Diary_response", "ESM_response","ESM_Detail", "time","timeString","AccessibilityTime", "NotificationTime","device_id"]
NewsdataKey = ["PhoneSessionID","AppSessionID", "startTime", "endTime", "StartTimestamp", "EndTimestamp", "dataType", "appName", "device_id"]

ESM_column = ["questionnaire_id", "isGenerate", "generateTime", "isRespond", "respondTime", "isSubmit",
              "submitTime", "isFinish", "ReplyCount", "TotalCount", "QuestionnaireType", "Q1(請問你在手機上使用了哪些平台？)", " ", "Q2(請問你在這（些）平台中「最近期」且「有印象」的一則新聞為何？)",
              " ", " ", "Q3(請問你有沒有對這則新聞從事下列行為？)", "Q4(請問這則新聞是由製作這則新聞的機構直接推送給你的嗎（例如：臉書上由新聞機構所推送的新聞，或透過新聞app看到的新聞）？)", 
              "Q5(請問是誰轉寄或分享給你的？)", " ", "Q6(請問你同不同意[帶入選擇的對象] （轉寄或分享這則新聞的人）對這則新聞的想法或態度？)",
              "Q7(請問你同不同意這則新聞所表達的立場？)", "Q8(請問這則新聞與哪個主題最相關？)", "Q9(請問當時使用手機看新聞的原因是什麼？（可複選）)",
              "Q10(請問你當時有多專注閱讀這則新聞？)", "Q11(請問你覺得你有多了解該則新聞的內容？)", "Q12(請問你相不相信這則新聞的內容？)",
              "Q13(請問你同不同意，這則新聞讓你想到自己的生活經驗？)", "Q14(請問你同不同意，這則新聞讓你想到其他重要社會議題？)", 
              "Q15(當你看到這則新聞時，請問你感到生氣的程度為何？)", "Q16(當你看到這則新聞時，請問你感到害怕的程度為何？)", "Q17(當你看到這則新聞時，請問你感到開心的程度為何？)", 
              "Q18(當你看到這則新聞時，請問你感到滿意的程度為何？)", "Q19(請問你同不同意：「你在看該則新聞時，有試圖找出新聞中的缺失（例如：內容會誤導人、來源不明確）」？)", 
              "Q20(請問當時你除了使用手機讀新聞外，同時還有做其他事情嗎（例如：處理家務、移動中、工作或學習、用餐、從事娛樂或休閒活動、與朋友聊天）？)", "Q21(請問當時你除了使用手機讀新聞外，同時還有做下列哪些事情？（可複選）)",
              " "]
Diary_column = ["questionnaire_id", "isGenerate", "generateTime", "isRespond", "respondTime", "isSubmit",
              "submitTime", "isFinish", "ReplyCount", "TotalCount", "QuestionnaireType", "Q1(請問你今天大約轉傳幾則新聞給別人？)", "Q2(請回想你今天轉傳新聞當中印象最深刻的一則，請問這則新聞與哪個主題最相關？)",
              "Q3(請問你透過什麼管道把這則新聞轉傳給別人？（可複選）)", "Q4(請問你轉傳這則新聞的主要對象是誰？（可複選）)", "Q5(請問你轉傳這則新聞給別人的原因是？（可複選）)",
              "Q6(請問今天有沒有碰到你懷疑內容有「錯誤」或者「會誤導人」的新聞？)", "Q7(請問這則內容可能有錯誤的新聞標題是什麼？)",
              "Q8(請問你透過什麼管道收到這則可能有錯誤的新聞？)", "Q9(請問這則可能有錯誤的新聞是誰轉寄或分享給你的？)", "Q10(請問你懷疑這則新聞可能含有錯誤資訊的原因是？（可複選）)",
              "Q11(請問你有沒有進一步確認這則新聞含有錯誤資訊?)", "Q12(請問你主要透過什麼方式來進一步確認這則新聞是否含有錯誤資訊？（可複選）)", "Q13(請問你看到新聞多久之後進一步確認這則新聞是否含有錯誤資訊？)",
              "Q14(針對這則有錯誤的新聞，請問你後續如何處理？（可複選）)", "Q15(請回想今天一整天在手機上所看到的新聞，你覺得今天最重要的「新聞事件」有哪些？)", " ", "Q16.1(這個事件與你自己的生活多相關？)", "Q16.2(這個事件與你自己的生活多相關？)"
              , "Q16.3(這個事件與你自己的生活多相關？)", "Q17.1(這個事件與整體社會多相關)", "Q17.2(這個事件與整體社會多相關)", "Q17.3(這個事件與整體社會多相關)", "Q18.1(請問你覺得[事件一]與[事件二]相關的程度有多強？)", "Q18.2(請問你覺得[事件二]與[事件三]相關的程度有多強？)"
              , "Q18.3(請問你覺得[事件一]與[事件三]相關的程度有多強？)", "Q19.1(請問你對於這個事件的想法或感覺有多正向？)", "Q20.1(請問你對於這個事件的想法或感覺有多負向？)", "Q19.2(請問你對於這個事件的想法或感覺有多正向？)", "Q20.2(請問你對於這個事件的想法或感覺有多負向？)"
              , "Q19.3(請問你對於這個事件的想法或感覺有多正向？)", "Q20.3(請問你對於這個事件的想法或感覺有多負向？)", "Q21(請問你今天有沒有跟別人談論或討論下列哪些事件?)"
              , " ", "Q22.1(請問你一起談論或討論的對象是誰？)", "Q23.1(你覺得你一起談論或討論的對象跟你的看法相不相同？)", "Q24.1(請問你是透過什麼方式跟別人談論或討論？（可複選）)",
              "Q22.2(請問你一起談論或討論的對象是誰？)", "Q23.2(你覺得你一起談論或討論的對象跟你的看法相不相同？)","Q24.2(請問你是透過什麼方式跟別人談論或討論？（可複選）)",
              "Q22.3(請問你一起談論或討論的對象是誰？)", "Q23.3(你覺得你一起談論或討論的對象跟你的看法相不相同？)", "Q24.3(請問你是透過什麼方式跟別人談論或討論？（可複選）)", "Q25(請問你今天從下列管道獲取新聞的時間有多少?)"]

Following_column = ["(請問你在「逐一帶入前面選項」時，同時還使用其他媒體嗎？（可複選）)", "(請問在當時，「帶入前面選項」與「用手機看新聞」哪個是主要活動？(需要優先完成、比較重要的活動))", 
                    "(請問在當時，「用手機看新聞」是為了「帶入前面選項」嗎？)", "(請問你（逐一帶入前面選項）已經花了多少時間？)", "(對你來說，請問（帶入前面選項）時，你感到無聊的程度為何？)",
                    "(對你來說，請問（帶入前面選項）時，你感到焦慮的程度為何？)", "(對你來說，請問（帶入前面選項）時，你感到開心的程度為何？)", "(對你來說，請問（帶入前面選項）時，你感到滿意的程度為何？)"]
ESM_following = 8


for i in range(7):
    for j in range(ESM_following):
        if 22 + j == 24:
            ESM_column.append(" ")
        ESM_column.append("Q" + str(22 + j) + "." + str(i + 1) + Following_column[j])
        
count = 0

@app.route("/home", methods=['POST', 'GET'])
def home():
    user = mongo.db.dump
    dataIndb = user.find({'device_id': "8bf875381c0c6f94"})
    for d in dataIndb:
        print(d["detectTimeHour"])
    return "ok"

def getnowtime():
    t = time.localtime()
    result = time.strftime("%m/%d/%Y, %H:%M:%S", t)
    return result
# user phone transfer context data to mongodb
@app.route("/dumpdata", methods=['POST'])
def index():
    #print("test")
    json_request = request.get_json(force=True, silent=True)
    #print(json_request)
        
    # for j in json_request['Accessibility']:
    #     print("readble : "+str(j['readable']))
    # user_id = json_request['device_id']
    # print("user_id : "+str(user_id))
#    f = open('log.txt', 'a')
    
#    f.write("start dumpdata: " + getnowtime() + "\n")
#    f.write(json_request['device_id'] + " in dumpdata\n")

    #print (str(json_request))
    
    user = mongo.db.dump
    
#    user.insert(json_request)
    
#    f.write("find dumpdata: " + getnowtime() + "\n")
#    IsInsert = False
    detectTimeHourIndb = []
    data = user.find({"$and":[{'device_id':json_request['device_id']},{'detectTimeHour':int(json_request['detectTimeHour'])}]})

#    f.write("insert dumpdata: " + getnowtime() + "\n")
    for d in data:
        detectTimeHourIndb.append(d["detectTimeHour"])
#        if "Battery" or "Connectivity" in d:
#            IsInsert = True
        
    if not json_request["detectTimeHour"] in detectTimeHourIndb:
        print(json_request['device_id'] + " insert " + str(json_request["detectTimeHour"]))
#        f.write("insert " + str(json_request["detectTimeHour"]) + " to db\n")
        user.insert(json_request)
    else:
        print(json_request['device_id'] + " has " + str(json_request["detectTimeHour"]) + " already")
#        if json_request['device_id'] == "357130089887875":
#            user.insert(json_request)
#        f.write(str(json_request["detectTimeHour"]) + " has in DB\n")
#        if IsInsert:
#            user.insert(json_request)


#    f.write("prepare dumpdata: " + getnowtime() + "\n")
#    else:
#        try:
#            if json_request["QuestionnaireAns"]:
#                d = {}
#                questionAns = json.dumps(json_request["QuestionnaireAns"])
#                ans = json.loads(questionAns, encoding='utf-8')
#                d["QuestionnaireAns"] = ans
#                d["device_id"] = json_request["device_id"]
#                d["user_id"] = json_request["user_id"]
#                d["timeString"] = json_request["timeString"]
#                d["detectTimeHour"] = json_request["detectTimeHour"]
#                d["uploadTimeHour"] = json_request["uploadTimeHour"]
#                user.insert(d)
#        except:
#            print("there is repeat data but not exist questionnaire")
        
    if(str(json_request) != None):
        
        allTimeStamp = dict()
        # user.insert(json_request)
        # user_id = request.args['id']
        # check all creationTime

        #data = user.find({'device_id': json_request['device_id']}) ###
        data = user.find({"$and":[{'device_id':json_request['device_id']},{'detectTimeHour':int(json_request['detectTimeHour'])}]})
#        for da in data:
#            print(da['detectTimeHour'])

#        f.write("prepare return message " + getnowtime() + "\n")
        
#        group = dict()
        for key in Key:
            if key == "QuestionnaireAns":
                if(key in json_request):
                    for targetObject in json_request[key]:
                        keyStr = key + ".timestamp"
                        questionnaire_id =  targetObject["questionnaire_id"]
                        #print("keystr : " + str(keyStr))
                        for question in targetObject["Questions"]:
                            #print("question: " + str(question))
                            #for item in data.distinct(keyStr):
                            #if item == question['timestamp']:
                            item = questionnaire_id + "+" + question["question_id"]
                            if key in allTimeStamp:
                                allTimeStamp[key].append(item)
                            else:
                                allTimeStamp[key] = [item]
                            #print("target time stamp : " + str(item))
            else:
                if(key in json_request):
                    keyStr = key + ".timestamp"
                    for item in data.distinct(keyStr):
                        if key in allTimeStamp:
                            allTimeStamp[key].append(item)
                        else:
                            allTimeStamp[key] = [item]
#                    for targetObject in json_request[key]: #bottleneck
#                        keyStr = key + ".timestamp"
#                        #print("keystr : " + keyStr)
#                        if key in allTimeStamp:
#                            allTimeStamp[key].append(targetObject['timestamp'])
#                        else:
#                            allTimeStamp[key] = [targetObject['timestamp']]
#                        for item in data.distinct(keyStr): #直接回傳json_request裡面的timestamp? or 用detectTimeHour去find
#                            if item == targetObject['timestamp']:
#                                if key in allTimeStamp:
#                                    allTimeStamp[key].append(item)
#                                else:
#                                    allTimeStamp[key] = [item]
                                #print("target time stamp : " + str(item))
        allTimeStamp['device_id'] = json_request['device_id']
        allTimeStamp['detectTimeHour'] = json_request['detectTimeHour']
        # for key in Key:
        #     user.aggregate([
        #      {'$group':{
        #      '_id': { 'readable': $readable, year: { $year: "$date" } },
        #     itemsSold: { $push:  { item: "$item", quantity: "$quantity" } }}}])

        message = json.dumps(allTimeStamp)
        
#        f.write("finish dumpdata: " + getnowtime() + "\n")
#        f.write("return message to " + str(json_request['device_id']) + "\n")
#        f.close()
        #print("message : " + str(message))
        # message = json.dumps({})

        # print("json_request not null" + str(json_request))
        # json_docs = {'error': "false"}
        return message

    else:
        json_docs = {'error': "true"}
#        f.write("return message error\n")
#        f.close()
        print(str(json_docs))
        return jsonify(json_docs)

# user data transfer session data to mongodb
@app.route("/newsdata", methods=['POST'])
def newsdata():
    json_request = request.get_json(force=True, silent=True)
    #print (str(json_request))
    if str(json_request['NewsData']) == None:
        json_docs = {'error': "true"}
        return jsonify(json_docs)
    
    res = dict()
    res['SessionID'] = []
    #print(res)
    for newsdata in json_request['NewsData']:
        #print(newsdata)
        device_id = newsdata['device_id']
        dataType = newsdata['dataType']
        #print(device_id + " in newsdata")
        for item in newsdata['data']:
            timestamp = item['timestamp']
            server_filename = item['fileName']
            filepath_list = item['filePath'].split('/')
            item['content'] = item['content'].strip()
            date = filepath_list[len(filepath_list) - 2]
            if dataType != 'Image':
                item['server_filename'] = server_filename
                item['server_filepath'] = device_id + "/" + date + "/" + server_filename
            else:
                item['server_filename'] = str(timestamp) + "-" + server_filename
                item['server_filepath'] = device_id + "/" + date + "/" + str(timestamp) + "-" + server_filename
            #print(item['server_filename'])
            #print(item['server_filepath'])
        #print("After insert server info:", json.dumps(json_dict))    
        data = mongo.db.newsdata
        users = data.find({"$and":[{'AppSessionID': newsdata['AppSessionID']}, {'device_id': device_id}]})
        #print(users)
        exist = False
        for user in users:
            #print(str(user['AppSessionID']) + " " + str(newsdata['AppSessionID']))
            if user['AppSessionID'] == newsdata['AppSessionID']:
                exist = True
                break
        if not exist:
            #print(str(res['SessionID']) + " " + str(newsdata['AppSessionID']))
            res['SessionID'].append(newsdata['AppSessionID'])
            data.insert(newsdata)
        
        #res['SessionID'] = newsdata['AppSessionID']
    f = open('log.txt', 'a')
    f.write("newsdata result: " + json.dumps(res) + "\n")  
    f.close()
    print("newsdata result: ", json.dumps(res))
    return json.dumps(res)

# check user phone is alive or not(send it every 30 minute)
@app.route('/isalive', methods=['POST', 'GET'], strict_slashes=False)
def isalive():
    
    json_request = request.get_json(force=True, silent=True)
    print(json_request['device_id'] + "in isalive")
    #print(json_request)
    user = mongo.db.isalive
    if(str(json_request) is None):
        json_docs = {'error': "sync error"}
        return json_docs

    else:
        data = dict()
#        missing_key = False
        for key in IsAliveKey:
            if key in json_request and key != 'device_id':
                data[key] = json_request[key]
                #print("key :"+ str(key))
                #print("data[key]" + str(data[key]))
            elif key not in json_request:
                print("something miss")
        #print("data" + str(data))
#        if missing_key:
        # file = open('MissingKeyData.txt', 'a')
        # file.write(str(json_request) + '\n')

        user.update({'device_id': json_request['device_id']}, {
                    '$set': data}, upsert=True, multi=True)

        return jsonify({'device_id': json_request['device_id']})

# store news url which on user phone to local    
@app.route("/savecsv/", methods = ["POST","GET"])
def input_csv():  #not used now
    if request.method == "POST":
        userid = request.form.get('userid')
        date = request.form.get('date')
        UrlCsv = request.files['UrlCsv']

        fpath = str(userid) + "/" + date + "/"
        
        try:
            os.makedirs(userid)
        # 檔案已存在的例外處理
        except FileExistsError:
            print("", end = "")
      
        try:
            os.makedirs(fpath)
        # 檔案已存在的例外處理
        except FileExistsError:
            print("", end = "")
        
        Txtpath = fpath + UrlCsv.filename;
        if not os.path.exists(Txtpath):
            UrlCsv.save(Txtpath)
            if os.path.isfile(Txtpath):
                return "UrlCsv upload success"
        else:
            TempPath = str(userid) + "/Temp.csv"
            UrlCsv.save(TempPath)
            ServerFile = open(Txtpath, 'a', encoding="utf-8")
            AndroidFile = open(TempPath, 'r', encoding="utf-8")
            ServerFile.write(AndroidFile.read())
            ServerFile.close()
            AndroidFile.close()
            return "UrlCsv upload success"
        return "Csv file uploaded failed"
    return "Csv file uploaded failed"

# store news url which on user phone to local    
@app.route("/savetxt/", methods = ["POST","GET"])
def input_txt():  #not used now
    if request.method == "POST":
        userid = request.form.get('userid')
        date = request.form.get('date')
        Txt = request.files['Txt']

        print(str(userid) + " " + str(date) + " " + str(Txt))
        
        fpath = str(userid) + "/" + date + "/"
        
        try:
            os.makedirs(userid)
        # 檔案已存在的例外處理
        except FileExistsError:
            print("", end = "")
      
        try:
            os.makedirs(fpath)
        # 檔案已存在的例外處理
        except FileExistsError:
            print("", end = "")
        
        Txtpath = fpath + Txt.filename;
        print(Txtpath)
        if not os.path.exists(Txtpath):
            Txt.save(Txtpath)
            if os.path.isfile(Txtpath):
                return "Txt upload success"
        else:
            TempPath = str(userid) + "/Temp2.txt"
            Txt.save(TempPath)
            ServerFile = open(Txtpath, 'a', encoding="utf-8")
            AndroidFile = open(TempPath, 'r', encoding="utf-8")
            ServerFile.write(AndroidFile.read())
            ServerFile.close()
            AndroidFile.close()
            return "Txt upload success"
        return "Text file uploaded failed"
    return "Text file uploaded failed"
       
# user phone send image to mongodb
@app.route('/getimg/', methods = ["POST","GET"])
def input_img():
    #data = {"userid":userid, "filename":filename}
    
    if request.method == "POST":
        #imgs = request.files.getlist()
        userid = request.form.get('userid')
#        f = open('log.txt', 'a')
#        f.write(userid + "in getimg ")
       
        #image_count = int(request.form.get('ImageCount'))
        #fpath = "D:\\Users\\MUILab-VR\\Desktop\\News Consumption\\" + userid + "\\"
        #if not os.path.exists(fpath):
        #    os.mkdir(fpath)
            
        #for i in range(0, image_count):
        imagefile = request.files['image']
        fname = request.form.get('filename')
        timestamp = request.form.get('timestamp')
        date = request.form.get('date')
        dtime = request.form.get('time')
        trigger = request.form.get('trigger')
        session = request.form.get('session_id')
        #fpath = "D:\\Users\\MUILab-VR\\Desktop\\News Consumption\\" + userid + "\\" + date + "\\"
        #if not os.path.exists(fpath):
        #    os.mkdir(fpath)
            
        #grid_fs = gridfs.GridFS(mongo.db)
        #id_ = grid_fs.put(imagefile, content_type = pimage.content_type, filename = imagefile.filename)
        
#        f.write(imagefile.filename + "\n")
#        f.close()
        if "Upload" in imagefile.filename:
            img = imagefile.filename[0:10] + imagefile.filename[17:]
        else:
            img = imagefile.filename
        
#        if "ESM" in img:
#            f = open('log.txt', 'a')
#            f.write(img + "\n")
#            f.close()
            
        mongo.save_file(userid + "-" + img, imagefile) # 12/14 id-2020-11-07-09-53-53-6-Facebook.jpg
        
        if not "Upload" in fname:
            img = imagefile.filename[0:10] + "-Upload-" + imagefile.filename[11:]
        else:
            img = fname
        
        if "ESM" in img:
            print(img)
            
        mongo.db[userid].insert_one({'userid': userid, "filename": img, "timestamp": timestamp, "date": date, "time": dtime, "trigger": trigger, "session_id": session})   
        #imagefile.save(fpath + timestamp + "-" + fname)
            
        
        #mongo.db[userid].insert_one({'userid': userid, "filename": fname, "timestamp": timestamp, "date": date, "time": dtime, "trigger": trigger})
    #print("Image Uploaded Successfully")
        return fname
    return "0"

# user phone send image to mongodb
@app.route('/upload_img/', methods = ["POST","GET"])
def upload_img():
    #data = {"userid":userid, "filename":filename}
    
    if request.method == "POST":
        #imgs = request.files.getlist()
        userid = request.form.get('userid')
#        f = open('log.txt', 'a')
#        f.write(userid + "in getimg ")
       
        #image_count = int(request.form.get('ImageCount'))
        #fpath = "D:\\Users\\MUILab-VR\\Desktop\\News Consumption\\" + userid + "\\"
        #if not os.path.exists(fpath):
        #    os.mkdir(fpath)
            
        #for i in range(0, image_count):
        imagefile = request.files['image']
        fname = request.form.get('filename')
        timestamp = request.form.get('timestamp')
        date = request.form.get('date')
#        dtime = request.form.get('time')
#        trigger = request.form.get('trigger')
#        session = request.form.get('session_id')
        
        #create device_id file
        user_root = str(userid)
        try:
            os.makedirs(user_root)
        except FileExistsError:
            pass
        
        #create each date file
        date_path = user_root + "/" + date
        try:
            os.makedirs(date_path)
        except FileExistsError:
            pass
        
        #construct image name
        if "Upload" in imagefile.filename:
            img = imagefile.filename[0:10] + imagefile.filename[17:]
        else:
            img = imagefile.filename
        img_name = timestamp + "-" + img
        
        #save image to specific file
        imagefile.save(date_path + "/" + img_name)
#        with open(date_path + "/" + img_name, "wb") as f:
#            f.write(imagefile)
        
        return imagefile.filename
    
    return "0"


@app.route('/selfTest/<string:userid>', methods=['POST','GET'])
def selfTest(userid=None):
    #讀取device id collection + fs.files檔名做比較
    Img_json = []
    Img_file = []
    
#    json_filename = mongo.db[userid].find({'date':'2021-01-25'})
#    for img in json_filename:
#        Img_json.append(img['filename'])
    
    path = "./" + userid
    allFileList = os.listdir(path)
    for file in allFileList:
        if file != "PhoneStateData" and file !=  "UserProgress":
            all_img = os.listdir(path + "/" + file)
            json_filename = mongo.db[userid].find({'date': file})
            Img_json = []
            Img_file = []
            for img in all_img:
                if img != "AllImg.txt" and img != "NewsUrl.csv":
                    img_new = img[13 + 1:13 + 11] + "-Upload" + img[13 + 11:]
                    #print(img_new)
                    Img_file.append(img_new)
                
            for img in json_filename:
                Img_json.append(img['filename'])
            
            count = 0
            for img in Img_json:
                if img not in Img_file:
                    pass
                else:
                    #print("In Img_file: " + img)
                    count += 1
            
            result = list(set(Img_file) - set(Img_json))
            #print(result)
            print(file + ": " + str(len(Img_file)) + "/" + str(len(Img_json)))
            print(file + ": " + str(len(set(Img_file))) + "/" + str(len(set(Img_json))))
#            print(count)
#    img_filename = mongo.db["fs.files"].find({'filename':{"$regex":userid + ".*"}})
#    for img in img_filename:
#        img_new = img['filename'][len(userid) + 1:len(userid) + 11] + "-Upload" + img['filename'][len(userid) + 11:]
#        print(img_new)
#        if img_new not in Img_json:
#            print(img_new + " not sync")
                

    return "OK"

# user check which images are in the mongodb and delete the repeat image in user phone
@app.route('/check_img/<string:userid>', methods=['POST'])
def check_img(userid=None):
    """
    predicts requested text whether it is ham or spam
    :return: json
    """
    
    ImgInDB = []
    if request.is_json:
        f = open('log.txt', 'a')
        f.write(userid + "in checkimg\n")
        
        
        print(userid + "in checkimg")
        #read json file post from android
        content = request.get_json()
        #f.write("user input: " + str(content[userid]) + "\n\n")
        #print("content: ", content) #{userID:[o,o,o,...]}
        #print("user img on phone: ", content[userid], " size: ", len(content[userid]))
        
        #read image in server and cut timestamp in file name
        ImgInServer = []
        path = str(userid)
        
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        
        allFileList = os.listdir(path)
        for file in allFileList:
            if file != "PhoneStateData" and file !=  "UserProgress" and file != "Temp.csv" and file != "Temp2.txt":
                all_img = os.listdir(path + "/" + file)
                for img in all_img:
                    if img != "AllImg.txt" and img != "NewsUrl.csv":
                        dash_index = img.find("-")
                        img_new = img[dash_index + 1:dash_index + 11] + "-Upload" + img[dash_index + 11:]
                        ImgInServer.append(img_new)
        
        #read all image in user's phone and cut Upload in file name
        User_All = []
        for user_img in content[userid]:
#            if "Upload" in user_img:
#                img_new = user_img[0:10] + user_img[17:]
#            else:
#                img_new = user_img
            User_All.append(user_img)
        
        f.write("User input(" + str(len(User_All)) + "): " + str(User_All) + "\n\n")
        
        ImgNotInDB_list = list(set(User_All) - set(ImgInServer))
        ImgInDB_list = list(set(User_All) - set(ImgNotInDB_list))
        
        #read this user's image in database
#        dbimg = mongo.db[userid].find({'userid': userid})
#        for img in dbimg:
#            ImgInDB.append(img['filename'])
#        
#        #take the image name which didn't in DB
#        ImgNotInDB_set = set(content[userid]) - set(ImgInDB)
#        ImgNotInDB_list = list(ImgNotInDB_set)
#        ImgInDB_list = list(set(content[userid]) - ImgNotInDB_set)
        #print("Image not in DB: ", ImgNotInDB, " size: ", len(ImgNotInDB))
        #return json object to android
        jsondict = {'NotInDB': ImgNotInDB_list, 'InDB': ImgInDB_list}
        jsonobj = json.dumps(jsondict)
        #print(str(ImgNotInDB_list))
        f.write("ImgNotInDB(" + str(len(ImgNotInDB_list)) + "): " + str(ImgNotInDB_list) + "\n\n")
        f.write("ImgInDB(" + str(len(ImgInDB_list)) + "): " + str(ImgInDB_list) + "\n\n")
        f.close()
    return str(jsonobj)

# user check which images are in the mongodb and delete the repeat image in user phone
@app.route('/checkimg/<string:userid>', methods=['POST'])
def check_image(userid=None):
    """
    predicts requested text whether it is ham or spam
    :return: json
    """
    ImgInDB = []
    if request.is_json:
        f = open('log.txt', 'a')
        f.write(userid + "in checkimg\n")
        
        
        print(userid + "in checkimg")
        #read json file post from android
        content = request.get_json()
        f.write("user input: " + str(content[userid]) + "\n\n")
        #print("content: ", content) #{userID:[o,o,o,...]}
        #print("user img on phone: ", content[userid], " size: ", len(content[userid]))
        
        #read this user's image in database
        dbimg = mongo.db[userid].find({'userid': userid})
        for img in dbimg:
            ImgInDB.append(img['filename'])
        
        #take the image name which didn't in DB
        ImgNotInDB_set = set(content[userid]) - set(ImgInDB)
        ImgNotInDB_list = list(ImgNotInDB_set)
        ImgInDB_list = list(set(content[userid]) - ImgNotInDB_set)
        #print("Image not in DB: ", ImgNotInDB, " size: ", len(ImgNotInDB))
        #return json object to android
        jsondict = {'NotInDB': ImgNotInDB_list, 'InDB': ImgInDB_list}
        jsonobj = json.dumps(jsondict)
        #print(str(ImgNotInDB_list))
        f.write("ImgNotInDB: " + str(ImgNotInDB_list) + "\n\n")
        f.write("ImgInDB: " + str(ImgInDB_list) + "\n\n")
        f.close()
    return str(jsonobj)

#transfer mongodb context data to csv and store in local
@app.route('/table/<string:userid>') 
def table(userid=None): #take the users phone data which in the mongodb
    
    save_dir = userid + "/PhoneStateData"
    try:
        os.makedirs(userid)
    # 檔案已存在的例外處理
    except FileExistsError:
        print("", end = "")
  
    try:
        os.makedirs(save_dir)
    # 檔案已存在的例外處理
    except FileExistsError:
        print("", end = "")
        
    Data = mongo.db.dump.aggregate([{'$match':{'device_id': userid}},{'$sort':{"detectTimeHour": 1}}], allowDiskUse=True)
    #Data = mongo.db.dump.find({'device_id': userid}).sort("detectTimeHour", 1)
    key_dict = {}
    key_number = {}
    for key in Key:
        key_dict[key] = False;
        key_number[key] = 0;
    #print(key_dict)
    
    for data in Data:
        for key in Key:
            '''
            if key == "QuestionnaireAns":
                print(data[key][0]["questionnaire_id"])
                
                Questionnaires = []
                Questionnaire_id = "0"
                json_str = json.dumps(data[key])
                dic_data = json.loads(json_str, encoding='utf-8')
                Not_questionArray = False
                for data in dic_data:
                    data_dic = {}
                    if not Not_questionArray:
                        data_dic["questionnaire_id"] = data["questionnaire_id"]  
                        data_dic["respondTime"] = data["respondTime"]  
                        data_dic["submitTime"] = data["submitTime"]  
                        data_dic["isFinish"] = data["isFinish"]
                        Not_questionArray = True
                        
                    Questions = []
                    Question_id = "1"
                    ques_dict = {}
                    for key,value in data.items():
                        
                        if data["questionnaire_id"] != Questionnaire_id:                        
                            Questionnaires.append(data_dic)
                            
                        else:
                            key != "questionnaire_id" and key != "respondTime" and key != "submitTime" and key != "isFinish":
                                
                
                json_str = json.dumps(data[key])
                dic_data = json.loads(json_str, encoding='utf-8')
                file_name = save_dir + "/" + userid + "_" + key + ".csv"
                csv_file = open(file_name, 'a', newline='', encoding='utf-8-sig')
                writer = csv.writer(csv_file, delimiter=',')
                
                if key_dict[key] == False:
                    for dic in dic_data:
                        keys = dic.keys()
                        # 寫入列名
                        #print(keys)
                        writer.writerow(keys)
                        break
                    key_dict[key] = True
                
                Questionnaire_id = 0
            '''
            if(key in data):               
                json_str = json.dumps(data[key])
                dic_data = json.loads(json_str, encoding='utf-8')
                key_number[key] += len(dic_data)
                keys = []
                file_name = save_dir + "/" + userid + "_" + key + ".csv"
                csv_file = open(file_name, 'a', newline='', encoding='utf-8-sig')
                writer = csv.writer(csv_file, delimiter=',')
                
#                count = 0
#                if key=="AppUsage" and count == 0:
#                    print(str(dic_data))
#                    count += 1
                    
                  
                if key_dict[key] == False:
                    count = 0  
                    for dic in dic_data:
                        if key=="AppUsage":
                            count += 1
                        if key=="AppUsage" and count == 2:
                            keys = dic.keys()
                            #print(keys)
                            # 寫入列名
                            #print(keys)
                            writer.writerow(keys)
                            break
                        elif key!="AppUsage":
                            keys = dic.keys()
                            #print(keys)
                            # 寫入列名
                            #print(keys)
                            writer.writerow(keys)
                            break
                    key_dict[key] = True
                    
                for dic in dic_data:
                
                    for key in keys:
                        if key not in dic:
                            dic[key] = 'NA'
                    #print(dic.values())
                    writer.writerow(dic.values())
                csv_file.close()
    print("{}'s phone state:". format(userid))
    for k,v in key_number.items():
        print("{} : {}". format(k,v))
        
    #--------------Encounter data--------------------------------
    Data = mongo.db.newsdata.find({'device_id': userid})
    key_dict = {}
    key_number = {}
    
    file_name = save_dir + "/" + userid + "_NewsData.csv"
    csv_file = open(file_name, 'a', newline='', encoding='utf-8-sig')
    writer = csv.writer(csv_file, delimiter=',')
    
    write_col = False;    
    if not write_col: 
        keys = NewsdataKey + ["Data Array"]
        writer.writerow(keys)
        write_col = True
        
    for data in Data:
        write_value = []
        for key in NewsdataKey:
            write_value.append(data[key])
        
        json_str = json.dumps(data['data'])
        dic_data = json.loads(json_str, encoding='utf-8')
    

        '''
        if len(data['data']) == 0:
            if not write_col: 
                keys = NewsdataKey + ["timestamp", "fileName", "filePath", "content", "server_filename", "server_filepath"]
                writer.writerow(keys)
                write_col = True
            writer.writerow(write_value)
            csv_file.close()
            continue;
        '''
        data_array = []
            
        for dic in dic_data:
            one_row = ""
            for k,v in dic.items():
                one_row = one_row + str(k) + " : " + str(v) + "    "                
            data_array.append(one_row)
        writer.writerow(write_value + data_array)
    csv_file.close()
    Questionnaire_list(userid)    
    return "OK"

#transfer mongodb image to local
@app.route('/StoreImgToLocal/<string:userid>')
def StoreImgToLocal(userid=None): #take the users picture which in the mongodb
    try:
        os.makedirs(userid)
    # 檔案已存在的例外處理
    except FileExistsError:
        print("")
        
    grid_fs = gridfs.GridFS(mongo.db)
    Images = mongo.db[userid].find({'userid': userid})
    
    
    for image in Images:
        image_name = image['filename']
        image_date = image['date']
        timestamp = image['timestamp']
        
        #image_file = bytes(url_for('file', filename = image_name))
        #image_file = mongo.send_file(image_name)
        
        #print(image_file)
        save_dir = userid + "/" + image_date #606/2020-08-03
        #print(save_dir + " >> " + image_name)
        try:
            os.makedirs(save_dir)
        # 檔案已存在的例外處理
        except FileExistsError:
            print("", end = "")
        
        
        image_name = image_name[0:10] + image_name[17:] # 12/14 2020-11-07-09-53-53-6-Facebook.jpg

        #image = grid_fs.files.find({'filename': image_name})
        for grid_out in grid_fs.find({'filename':userid + "-" + image_name}): # 12/14 id-2020-11-07-09-53-53-6-Facebook.jpg
            #print(image_name)
            image = grid_out.read()
            #print(image)
            #base64_data = codecs.encode(image, 'base64')
            #image = base64_data.decode('utf-8')
            f = open(save_dir + "/" + timestamp + "-" + image_name, "wb")
            f.write(image)
            f.close()
            
            collection = mongo.db.fs.files
            result = collection.find_one({'filename':  userid + "-" + image_name}) # 12/14 id-2020-11-07-09-53-53-6-Facebook.jpg
            _id = result['_id']
            fs = gridfs.GridFS(mongo.db)
            fs.delete(_id)
        #image.save(save_dir + "/" + timestamp + "-" + image_name)
        
    return "OK"

from collections import defaultdict
@app.route('/progress/<string:device_id>') 
def progress(device_id=None):
    try:
        os.makedirs(device_id + "/UserProgress")
    # 檔案已存在的例外處理
    except FileExistsError:
        print("",end="")
        
    load_dict = mongo.db.dump.aggregate([{'$match':{'device_id': device_id}},{'$sort':{"detectTimeHour": 1}}], allowDiskUse=True)
    #load_dict = mongo.db.dump.find({'device_id': device_id}).sort("detectTimeHour", 1).allowDiskUse()
    Dump_Y = defaultdict(list)
    Dump_X = []
    
#     print("Writing", end="")

#     for data_obj in load_dict:
#         Y_dict = dict()
#         for key in DumpKey:
#             try:
#                 Y_dict[key] = len(data_obj[key])
#             except KeyError:
#                 Y_dict[key] = 0
#         Y.append(Y_dict)
#         X.append(data_obj["detectTimeHour"])
#         print(Y_dict)
#         print("------------------------------")
#     print(X)

    #dump data(For day)
    """
    OneDay_dump = 0
    lastdetectTimeHour = 0
    for data_obj in load_dict:
        detectTimeHour = data_obj["detectTimeHour"]
    
        if lastdetectTimeHour != 0 and lastdetectTimeHour//100 != detectTimeHour//100:
            Dump_Y.append(OneDay_dump)
            Dump_X.append(lastdetectTimeHour//100)
            OneDay_dump = 0
        try:
            OneDay_dump += len(data_obj["myAccessibility"])
        except KeyError:
            OneDay_dump += 0
        
        lastdetectTimeHour = detectTimeHour
        
    Dump_Y.append(OneDay_dump)
    Dump_X.append(lastdetectTimeHour//100)
    """
    
    #dump data(For hour)
    for data_obj in load_dict:
        detectTimeHour = data_obj["detectTimeHour"]
        for key in Key:
            try:
                Dump_Y[key].append(len(data_obj[key]))
            except KeyError:
                Dump_Y[key].append(0)
        Dump_X.append(str(detectTimeHour))
    
    x_axis = [Dump_X[d] for d in range(0, len(Dump_X), 12)]
    x_axis.append(Dump_X[len(Dump_X) - 1])

    for k, v in Dump_Y.items():
        trace = go.Scatter(x=Dump_X, y=v, name=k)
        layout = plotly.graph_objs.Layout(xaxis=dict(type='category', title="hour", tickmode='array', tickvals = np.arange(0,len(Dump_X),12),ticktext=x_axis), yaxis = {'title':"data number"})                                                                                  
        fig = plotly.graph_objs.Figure([trace], layout)      
                                                                      
        py.offline.plot(fig,filename=device_id+"/UserProgress/" + k + ".html")
    
    #esm data
    load_dict = mongo.db.isalive.find({'device_id': device_id})[0]

    ESM_Y = []
    ESM_Z = []
    ESM_X = []
    for data_obj in load_dict["ESM_Detail"]:
        ESM_Y.append(int(data_obj["Today_Response"]))
        ESM_Z.append(int(data_obj["Total_count"]))
        date_split = data_obj["Date"].split("/")
        ESM_X.append(date_split[1] + "/" + date_split[2])
    x = np.arange(len(ESM_Z))  # the label locations
    width = 0.35  # the width of the bars
    plt.figure(dpi=100)
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, ESM_Y, width, label='Response')
    rects2 = ax.bar(x + width/2, ESM_Z, width, label='Total')
    ax.set_ylabel('date')
    ax.set_xlabel('esm number')
    ax.set_xticks(x)
    ax.set_xticklabels(ESM_X)
    ax.legend()
    plt.savefig(device_id+'/UserProgress/EsmTrend.png')
    """
    plt.figure(dpi=100)
    plt.bar(ESM_X, ESM_Y, width = 1.0)
    plt.xlabel("date", fontsize=10, labelpad = 10)
    plt.ylabel("esm number", fontsize=10, labelpad = 15)
    plt.savefig(device_id+'/UserProgress/EsmTrend.png')
    """
    #img data
    img_Y = []
    img_X = []
    rootdir = device_id
    list_dir = sorted(os.listdir(rootdir))
    for img_date in list_dir:
        if img_date != "PhoneStateData" and img_date != "UserProgress":
           img_Y.append(len(os.listdir(rootdir + "/" + img_date)))
           date_split = img_date.split("-")
           img_X.append(date_split[1] + "/" + date_split[2])
    plt.figure()
    plt.bar(img_X, img_Y, width = 1.0)
    plt.xlabel("date", fontsize=10, labelpad = 10)
    plt.ylabel("img number", fontsize=10, labelpad = 15)
    plt.savefig(device_id+'/UserProgress/ImgTrend.png')
    
    return "OK"

@app.route('/api') 
def GetDataToReact(device_id=None): 
#    print("global device id: " + global_device_id)
#    with open('UserData.json', 'r') as f:
#        return json.dumps(json.load(f))
    
    load_dict = mongo.db.dump.aggregate([{'$match':{'device_id': global_device_id}},{'$sort':{"detectTimeHour": 1}}], allowDiskUse=True)
    Dump_Y = defaultdict(list)
    Dump_X = []
    Dump_content = []
    
    for data_obj in load_dict:
        content = {}
        content["detectTimeHour"] = data_obj["detectTimeHour"]
        for key in Key:
            try:
                content[key] = len(data_obj[key])
            except KeyError:
                content[key] = 0
        Dump_content.append(content)
    return json.dumps(Dump_content)

from bson.json_util import dumps

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(os.path.join('watch-data-table-master','build','static'), path)

@app.route('/progress_dump/<string:device_id>') 
def ProgressTable(device_id=None):  
    global global_device_id 
    global_device_id = device_id
    print(global_device_id)
    return app.send_static_file('index.html')
#    load_dict = mongo.db.dump.aggregate([{'$match':{'device_id': device_id}},{'$sort':{"detectTimeHour": 1}}], allowDiskUse=True)
#
#    Dump_content = defaultdict(list)
#    #dump data(For hour)
#    labels = [" "] + Key
#    for data_obj in load_dict:
#        detectTimeHour = data_obj["detectTimeHour"]
#        for key in Key:
#            try:
#                Dump_Y[key].append(len(data_obj[key]))
#            except KeyError:
#                Dump_Y[key].append(0)
#        Dump_X.append(int(detectTimeHour))
#    
#    df = DataFrame(Dump_Y)
#    df.index = Dump_X
#    for i in range(len(Dump_X)):
#        Dump_content[Dump_X[i]] = df.loc[Dump_X[i]].tolist()

@app.route('/progress_data/<string:device_id>') 
def ProgressHtml(device_id=None):
    #esm data
    load_dict = mongo.db.isalive.find({'device_id': device_id})[0]

    ESM_Y = []
    ESM_Z = []
    ESM_X = []
    esm_content = defaultdict(list)
    for data_obj in load_dict["ESM_Detail"]:
        ESM_Y.append(int(data_obj["Today_Response"]))
        ESM_Z.append(int(data_obj["Total_count"]))
        date_split = data_obj["Date"].split("/")
        if len(date_split[1]) < 2:
            date_split[1] = "0" + date_split[1]
        if len(date_split[2]) < 2:
            date_split[2] = "0" + date_split[2]
        ESM_X.append(date_split[1] + "/" + date_split[2])
    for i in range(len(ESM_X)):
        esm_content[ESM_X[i]] = [ESM_Y[i], ESM_Z[i]]
        
    #img data
    img_Y = []
    img_X = []
    img_content = defaultdict(list)
    rootdir = device_id
    list_dir = sorted(os.listdir(rootdir))
    for img_date in list_dir:
        if img_date != "PhoneStateData" and img_date != "UserProgress":
            img_Y.append(len(os.listdir(rootdir + "/" + img_date)) - 2)
            date_split = img_date.split("-")
            img_X.append(date_split[1] + "/" + date_split[2])
    for i in range(len(img_X)):
        img_content[img_X[i]] = [img_Y[i]]
        
    #return send_from_directory(app.static_folder, "index.html")
    return render_template('form.html', esm_labels = [" ", "Today_Response", "Total_Count"], esm_content = esm_content, img_labels = [" ", "Picture_number"], img_content = img_content)

def isDiary(row):
    if row[0] == "1" and (row[6] == "有" or row[6] == "沒有"):
        return True
    return False

def ESMcoltoCsv(device_id):
    with open(device_id + "/PhoneStateData/" + device_id + "_ESM.csv", 'a', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(ESM_column)


def DiarycoltoCsv(device_id):
    with open(device_id + "/PhoneStateData/" + device_id + "_Diary.csv", 'a', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(Diary_column)
        
def Questionnaire_list(device_id):
    file_name = device_id + "/PhoneStateData/" + device_id + "_QuestionnaireAns.csv"
    
    ESMcoltoCsv(device_id)
    DiarycoltoCsv(device_id)
    ESM_data =  [ [""]*80 for i in range(200)]
    Diary_data =  [ [""]*80 for i in range(200)]
    data = [ [] for i in range(200)]
    D_data = [ [] for i in range(200)]
    questionnaire_check = [False]*1000
    diary_check = [False]*1000
# 開啟 CSV 檔案
    with open(file_name, "r" , newline='', encoding="utf-8-sig") as csvfile:
        # 讀取 CSV 檔案內容
        rows = csv.reader(csvfile)
      
        next(rows) 
        # 以迴圈輸出每一列
        #index = 0
        data_index = 0
        for row in rows:
            questionnaire_index = int(row[0])
            #print(str(questionnaire_index) + " " + str(data_index))
            
            if row[10] == "ESM":
                if not questionnaire_check[questionnaire_index]:
                    data[questionnaire_index] = row[0:11]
                    #print("ESM index: " + str(questionnaire_index))
                    #questionnaire_check[questionnaire_index] = True
            else:
                if not diary_check[questionnaire_index]:
                    D_data[questionnaire_index] = row[0:11]
                    #print("diary index: " + str(questionnaire_index))
                    #diary_check[questionnaire_index] = True
                #questionnaire_check.append(False)
            all_questions = row[11][1:-1]
            indices = [0] + [m.start() + 1 for m in re.finditer('}', all_questions)]
            questions = [all_questions[i + 2:j] for i,j in zip(indices, indices[1:]+[None])]
            questions[0] = "{'" + questions[0]
            questions = questions[:-1]
 
            if row[10] == "ESM":
                for question in questions:
                    question_dict  = eval(question)#字串轉dict
                    #data.append(question_dict["answer_choice"].strip())
                                       
                    if question_dict["question_id"] == "0":
                        question_index = int(question_dict["question_id"])
                        ESM_data[questionnaire_index][question_index] = question_dict["answer_choice"].replace("\r\n","").replace("\n","")
                    else:
                        question_index = int(question_dict["question_id"]) - 1
                        ESM_data[questionnaire_index][question_index] = question_dict["answer_choice"].strip().replace("\r\n","").replace("\n","")
                    
                    #print(str(question_index) + " " + ESM_data[questionnaire_index][question_index])

#                    if question_dict["answer_choice"].strip() == "用手機看新聞":
#                        data.append("")
#                with open(device_id + "/PhoneStateData/" + device_id + "_ESM.csv", 'a', newline='') as csvFile:
#                    writer = csv.writer(csvFile)
#                    writer.writerow(data)
                
            else:
                print("questionnaire id: " + str(questionnaire_index))
                for question in questions:
                    question_dict  = eval(question)#字串轉dict
                    
                    if question_dict["question_id"] == "0":
                        question_index = int(question_dict["question_id"])
                        Diary_data[questionnaire_index][question_index] = question_dict["answer_choice"].replace("\r\n","").replace("\n","")
                    else:
                        question_index = int(question_dict["question_id"]) - 1
                        ans = question_dict["answer_choice"].strip().replace("\r\n","").replace("\n","")
                        if question_index == 0 and ans == "":
                            Diary_data[questionnaire_index][question_index] = " "
                        else:
                            Diary_data[questionnaire_index][question_index] = question_dict["answer_choice"].strip().replace("\r\n","").replace("\n","")
                        
                print(Diary_data[questionnaire_index])

                    #data.append(question_dict["answer_choice"].strip())
#                    if question_dict["question_id"] == '55' or question_dict["question_id"] == '56' or question_dict["question_id"] == '57' or question_dict["question_id"] == '58':
#                        col_name = "Q" + str(int(question_dict["question_id"]) - 42) #13
#                        last_four_ques[col_name] = question_dict["answer_choice"]
#                    else:
#                        data.append(question_dict["answer_choice"].strip())
#                for i in range(len(data), index):#再Q13前要放幾個空白
#                    data.append("")
#                if len(last_four_ques) == 3:#如果Q13是空的
#                    data.append("")
#                for key, value in last_four_ques.items():                    
#                    data.append(value.strip())
                
#                with open(device_id + "/PhoneStateData/" + device_id + "_Diary.csv", 'a', newline='') as csvFile:
#                    writer = csv.writer(csvFile)
#                    writer.writerow(data)
                
                #print(row[11])
            #print(data)
            data_index += 1
    data = [x for x in data if x != []]
    D_data = [x for x in D_data if x != []]
    ESM_data = [x for x in ESM_data if x != [""]*80]
    Diary_data = [x for x in Diary_data if x != [""]*80] #//
    #print(D_data)
    #print(Diary_data)
    i = 0
    for data_list in ESM_data:
        data_list = data[i] + data_list
        with open(device_id + "/PhoneStateData/" + device_id + "_ESM.csv", 'a', newline='', encoding="utf-8-sig") as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(data_list)
        i += 1
        
    i = 0
#    except:
#        print("Something happen in Questionnaire_list")
    for data_list in Diary_data:
        try:
            data_list = D_data[i] + data_list
            print(data_list)
            with open(device_id + "/PhoneStateData/" + device_id + "_Diary.csv", 'a', newline='', encoding="utf-8-sig") as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(data_list)
            i += 1
        except:
            print("finish all")

    
# running web app in local machine
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=28017, threaded=True)
    #http_server = WSGIServer(('140.113.214.150', 28017), app)
    #http_server.serve_forever()

