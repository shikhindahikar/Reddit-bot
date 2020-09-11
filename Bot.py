# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 00:01:31 2020

@author: SHIKHIN
"""
from __future__ import division
import praw
import datetime
from statistics import mean
import re
from pytz import timezone
import operator

tz = timezone('EST')
grade_types = {'PO01':1, 'FR02':2, 'AG03':3, 'G04':4, 'G06':6, 'VG08':8, 'VG10':10, 'F12':12, 'F15':15, 'VF20':20, 'VF25':25, 'VF35':35, 'VF30':30, 'XF40':40, 'XF45':45, 'AU50':50, 'AU53':53, 'AU55':55, 'AU58':58, 'MS60':60, 'MS61':61, 'MS62':62, 'MS63':63, 'MS64':64, 'MS65':65, 'MS66':66, 'MS67':67, 'MS68':68, 'MS69':69, 'MS70':70, 'PO':1, 'po':1, 'Poor':1, 'poor':1, 'FR':2, 'fr':2, 'AG':3, 'ag':3, 'G':4, 'g':4, 'Good':4, 'good':4, 'VG':8, 'vg':8, 'F':12, 'f':12, 'Fine':12, 'fine':12, 'VF':20, 'vf':20, 'XF':40, 'xf':40, 'AU':50, 'au':50, 'BU':60, 'bu':60, 'MS':60, 'ms':60, 'PF':60, 'pf':60}

alt_grade_types = ['PO', 'po', 'Poor', 'poor', 'FR', 'fr', 'AG', 'ag', 'G', 'g', 'Good', 'good', 'VG', 'vg', 'F', 'f', 'Fine', 'fine', 'VF', 'vf', 'XF', 'xf', 'au', 'AU','BU', 'bu', 'MS', 'ms', 'pf', 'PF']

numeric_grade_type = [1, 2, 3, 4, 6, 8, 10, 12, 15, 20, 25, 35, 30, 40, 45, 50, 53, 55, 58, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70 ]

desig_set1 = ['FS', 'FB', 'FH', 'FBL']
desig_set2 = ['PL', 'DMPL']
desig_set3 = ['CAM', 'DCAM']
desig_set4 = ['BR', 'RD', 'RB']
desig_set5 = ['toned', 'cleaned', 'polished', 'details', 'replated', 'corroded']
desig_set6 = ['+', '*']

reddit = praw.Reddit("bot", user_agent="bot user agent")

subreddit=reddit.subreddit('redditCoinGrading')

def search_avg_grade(avg):
    for key in grade_types:
        if(grade_types[key] == avg):
            return key
        elif(grade_types[key] >= avg):
            return key


grade_list = []             #contains grades of different comments

while(True):

    for submission in subreddit.new():
            
            desig_dict1 = {'FS':0, 'FB':0, 'FH':0, 'FBL':0}
            desig_dict2 = {'PL':0, 'DMPL':0}
            desig_dict3 = {'CAM':0, 'DCAM':0}
            desig_dict4 = {'BR':0, 'RD':0, 'RB':0}
            desig_dict5 = {'toned':0, 'cleaned':0, 'polished':0, 'details':0, 'replated':0, 'corroded':0}
            desig_dict6 = {'+':0, '*':0}



            converted_submission_dt = datetime.datetime.utcfromtimestamp(submission.created_utc)
            current_time_utc = datetime.datetime.utcnow()

            date_difference = current_time_utc - converted_submission_dt

            if(date_difference.days <= 7):
                bot_in_post = False                                 #flag if bot has commented on the post

                for comment in submission.comments:
                    if ((comment.author is not None) and (comment.author.name=="RCG_bot")):
                        bot_in_post = True
                        break

                if(bot_in_post==False):
                    mycomment = submission.reply("Hi, I’m the RCG bot (beta)!\n\nPlease read the rules how to have your grade counted.\n\nThank you, and happy collecting!\n\n ^(*I'm a bot and this action was performed automatically. Please [contact the moderators](https://www.reddit.com/message/compose/?to=/r/redditcoingrading) or [fill out this form](https://forms.gle/HtoDquWoqRAy9DWdA) if there is a bug*)")
                    mycomment.mod.distinguish(how='yes', sticky=True)


                numeric_grade = []
                designation = []
                
                for comment in submission.comments:
                    
                    set1 = False
                    set2 = False
                    set3 = False
                    set4 = False
                    set5 = False
                    set6 = False

                for comment in submission.comments:
                    if (comment.score >= 0 and  comment.id and (comment.author is not None) and (comment.author.name!="RCG_bot")):            #use author name, improve bot using this functionality
                        curr_comment = comment.body
                        sub_str = re.findall(r'\[(.*?)\]', curr_comment)
                        if(sub_str):
                            number_metric = re.findall('[0-9]+', sub_str[0])

                            if(number_metric):
                                numeric_grade.append(int(number_metric[0]))
                            else:
                                for alt in alt_grade_types:
                                    if(alt in sub_str[0].lower()):                      #po and poor bug
                                        if((alt=='po' and 'poor' in sub_str[0].lower()) or (alt=='f' and 'fine' in sub_str[0].lower()) or (alt=='f' and 'vf' in sub_str[0].lower()) or (alt=='g' and 'vg' in sub_str[0].lower()) or (alt=='f' and 'xf' in sub_str[0].lower()) or (alt=='f' and 'pf' in sub_str[0].lower())):
                                            continue
                                        else:
                                            numeric_grade.append(grade_types[alt])


                        if(sub_str):
                            if(set1 is False):
                                for s in desig_set1:
                                    if(s.lower() in sub_str[0].lower()):
                                        if(not(s=='FB' and 'fbl' in sub_str[0].lower())):
                                            designation.append(s)
                                            desig_dict1[s] = desig_dict1[s] + 1
                                            set1 = True
                                            break
                            
                            if(set2 is False):
                                for s in desig_set2:
                                    if(s.lower() in sub_str[0].lower()):
                                        if(not(s=='PL' and 'dmpl' in sub_str[0].lower())):        
                                            designation.append(s)
                                            desig_dict2[s] = desig_dict2[s] + 1
                                            set2 = True
                                            break
                                
                            if(set3 is False):
                                for s in desig_set3:
                                    if(s.lower() in sub_str[0].lower()):
                                        if(not(s=='CAM' and 'dcam' in sub_str[0].lower())):
                                            designation.append(s)
                                            desig_dict3[s] = desig_dict3[s] + 1
                                            set3 = True
                                            break
                                    
                            if(set4 is False):
                                for s in desig_set4:
                                    if(s.lower() in sub_str[0].lower()):
                                        designation.append(s)
                                        desig_dict4[s] = desig_dict4[s] + 1
                                        set4 = True
                                        break
    
                            if(set5 is False):
                                for s in desig_set5:
                                    if(s in sub_str[0].lower()):
                                        designation.append(s)
                                        desig_dict5[s] = desig_dict5[s] + 1
                                        set5 = True
                                        break
    
                            if(set6 is False):
                                for s in desig_set6:
                                    if(s in sub_str[0]):
                                        designation.append(s)
                                        desig_dict6[s] = desig_dict6[s] + 1
                                        set6 = True
                                        break
                        

                        del sub_str[:]
                        
                        desig_final = []
                        
                        if(desig_dict1[max(desig_dict1.items(), key=operator.itemgetter(1))[0]]!=0):
                            desig_final.append(max(desig_dict1.items(), key=operator.itemgetter(1))[0])
                        
                        if(desig_dict2[max(desig_dict2.items(), key=operator.itemgetter(1))[0]]!=0):
                            desig_final.append(max(desig_dict2.items(), key=operator.itemgetter(1))[0])
                        
                        if(desig_dict3[max(desig_dict3.items(), key=operator.itemgetter(1))[0]]!=0):
                            desig_final.append(max(desig_dict3.items(), key=operator.itemgetter(1))[0])
                        
                        if(desig_dict4[max(desig_dict4.items(), key=operator.itemgetter(1))[0]]!=0):
                            desig_final.append(max(desig_dict4.items(), key=operator.itemgetter(1))[0])
                        
                        if(desig_dict5[max(desig_dict5.items(), key=operator.itemgetter(1))[0]]!=0):
                            desig_final.append(max(desig_dict5.items(), key=operator.itemgetter(1))[0])
                        
                        if(desig_dict6[max(desig_dict6.items(), key=operator.itemgetter(1))[0]]!=0):
                            desig_final.append(max(desig_dict6.items(), key=operator.itemgetter(1))[0])
                        
                        print(desig_final)


                print(numeric_grade)

                for num in numeric_grade:
                    if(num not in numeric_grade_type):
                        numeric_grade.remove(num)

                if(numeric_grade):                             #control block which edits comment
                    average = mean(numeric_grade)
                    print(average)
                    final_avg = search_avg_grade(average)                 #finds the correspoding key in grade_types
                    
                    listToStr = ' '.join([str(elem) for elem in desig_final])
                    
                    edited_comment = "Hi, I’m the RCG bot (beta)!\n\n" + "This coin grades as follows: \n #" + final_avg + " " + listToStr + "\n\nPlease read the rules how to have your grade counted.\n\n " + "\n\n^(*Last updated*: *" + datetime.datetime.now(tz).strftime('%m/%d/%y %I:%M:%S %p') + " EST*) \n\n ^(*I'm a bot and this action was performed automatically. Please [contact the moderators](https://www.reddit.com/message/compose/?to=/r/redditcoingrading) or [fill out this form](https://forms.gle/HtoDquWoqRAy9DWdA) if there is a bug*)"

                    if(date_difference.days == 7):
                        edited_comment = edited_comment + "\n\n^(This post is more than 7 days old, and will no longer be updated.)"

                    for comment in submission.comments:
                        if (comment.author is not None and comment.author.name=="RCG_bot"):
                            reddit.validate_on_submit = True
                            reddit.comment(comment.id).edit(edited_comment)
                            break




