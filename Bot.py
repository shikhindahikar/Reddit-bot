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

tz = timezone('EST')
grade_types = {'PO01':1, 'FR02':2, 'AG03':3, 'G04':4, 'G06':6, 'VG08':8, 'VG10':10, 'F12':12, 'F15':15, 'VF20':20, 'VF25':25, 'VF35':35, 'VF30':30, 'XF40':40, 'XF45':45, 'AU50':50, 'AU53':53, 'AU55':55, 'AU58':58, 'MS60':60, 'MS61':61, 'MS62':62, 'MS63':63, 'MS64':64, 'MS65':65, 'MS66':66, 'MS67':67, 'MS68':68, 'MS69':69, 'MS70':70, 'PO':1, 'po':1, 'Poor':1, 'poor':1, 'FR':2, 'fr':2, 'AG':3, 'ag':3, 'G':4, 'g':4, 'Good':4, 'good':4, 'VG':8, 'vg':8, 'F':12, 'f':12, 'Fine':12, 'fine':12, 'VF':20, 'vf':20, 'XF':40, 'xf':40, 'AU':50, 'au':50, 'BU':60, 'bu':60, 'MS':60, 'ms':60}

alt_grade_types = ['PO', 'po', 'Poor', 'poor', 'FR', 'fr', 'AG', 'ag', 'G', 'g', 'Good', 'good', 'VG', 'vg', 'F', 'f', 'Fine', 'fine', 'VF', 'vf', 'XF', 'xf', 'au', 'AU','BU', 'bu', 'MS', 'ms']

numeric_grade_type = [1, 2, 3, 4, 6, 8, 10, 12, 15, 20, 25, 35, 30, 40, 45, 50, 53, 55, 58, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70 ]

reddit = praw.Reddit("bot", user_agent="bot user agent")

track_comments = []

subreddit=reddit.subreddit('testingground4bots')

class sub_track:                            #to track bot's comment on a post
    
    def __init__(self, submission_id, Mycomment_id):  
        self.submission_id = submission_id  
        self.Mycomment_id = Mycomment_id 
    
def remove_brackets(metric_list):                   #removes square brackets
    for i in range(len(metric_list)):
        str(metric_list[i]).strip('[]')
        
def remove_comment_id(submission, id_list):
    for comment in submission.comment:
        if(comment.id in id_list):
            id_list.remove(comment.id)

def search_avg_grade(avg):
    for key in grade_types:
        if(grade_types[key] == avg):
            return key
        elif(grade_types[key] >= avg):
            return key

    
submission_track = []       #tracks submissions which have been replied to and are less than or 3 days old
grade_list = []             #contains grades of different comments
    
while(True):
    
    for submission in subreddit.new():
        
            
            
            converted_submission_dt = datetime.datetime.utcfromtimestamp(submission.created_utc)
            current_time_utc = datetime.datetime.utcnow()
            
            date_difference = current_time_utc - converted_submission_dt
            
            in_list = False
            
            if(date_difference.days <= 4):
                for old_submission in submission_track :           #check if this post has already been checked by bot
                    
                    if(old_submission.submission_id == submission.id):
                        in_list = True
                        break
                
                if(not in_list):
                    mycomment = submission.reply("Hi, I’m the RCG bot (Beta)!\n\nThis comment will be updated every five minutes to include the rounded average of the grades submitted by the community.\n\nTo have your grade counted, please put your grade and designation in square brackets, like this: [MS62 rd] [xf40 cleaned] [f12+] etc, and continue writing any other descriptions and opinions outside the brackets.\n\nThank you, and happy collecting!\n\n ^(*I'm a bot and this action was performed automatically. Please [contact the moderators](https://www.reddit.com/message/compose/?to=/r/redditcoingrading) or [fill out this form](https://forms.gle/HtoDquWoqRAy9DWdA) if there is a bug*)")
                    #mycomment.mod.distinguish(how='yes', sticky=True)               #distinguishes as a mod and sticks the comment
                    comment_id = mycomment.id
                    track_comments.append(comment_id)                       #tracking comment to edit
                    obj = sub_track(submission.id, comment_id)              #creating objects for  tracking
                    submission_track.append(obj)
                    
                    
                metric_list = []
                numeric_grade = []
                
                for comment in submission.comments:
                    if (comment.score >= 0 and  comment.id and (comment.id not in track_comments) and (comment.author is not None and comment.author.name.lower()!="rcg_bot")):            #use author name, improve bot using this functionality 
                        curr_comment = comment.body
                        sub_str = re.findall(r'\[(.*?)\]', curr_comment)
                        if(sub_str):
                            number_metric = re.findall('[0-9]+', sub_str[0])
                        
                            if(number_metric):
                                numeric_grade.append(int(number_metric[0]))
                            else:
                                for alt in alt_grade_types:
                                    if(alt in sub_str[0]):                      #po and poor bug
                                        if((alt=='po' and 'poor' in sub_str[0]) or (alt=='f' and 'fine' in sub_str[0]) or (alt=='F' and 'Fine' in sub_str[0]) or (alt=='F' and 'VF' in sub_str[0]) or (alt=='f' and 'vf' in sub_str[0]) or (alt=='G' and 'VG' in sub_str[0]) or (alt=='g' and 'vg' in sub_str[0]) or (alt=='F' and 'XF' in sub_str[0]) or (alt=='f' and 'xf' in sub_str[0])):
                                            continue    
                                        else: 
                                            numeric_grade.append(grade_types[alt])
                                        
                            
                
                        del sub_str[:]
                        
                
                print(numeric_grade)
                
                for num in numeric_grade:
                    if(num not in numeric_grade_type):
                        numeric_grade.remove(num)
                
                if(numeric_grade):                             #control block which edits comment
                    average = int(mean(numeric_grade))
                    print(average)
                    final_avg = search_avg_grade(average)                 #finds the correspoding key in grade_types
                    edited_comment = "Hi, I’m the RCG bot (Beta)!\n\n" + "This coin, according to the community, grades as follows: \n #" + final_avg +"\n\nThis comment will be updated every five minutes to include the rounded average of the grades submitted by the community.\n\nTo have your grade counted, please put your grade and designation in square brackets, like this: [MS62 rd] [xf40 cleaned] [f12+] etc, and continue writing any other descriptions and opinions outside the brackets.\n\nThank you, and happy collecting!\n\n " + "\n\n*Last updated*: *" + datetime.datetime.now(tz).strftime('%m/%d/%y %I:%M:%S %p') + " EST* \n\n ^(*I'm a bot and this action was performed automatically. Please [contact the moderators](https://www.reddit.com/message/compose/?to=/r/redditcoingrading) or [fill out this form](https://forms.gle/HtoDquWoqRAy9DWdA) if there is a bug*)"
                    
                    if(date_difference.days == 4):
                        edited_comment = edited_comment + "*\nThis post is more than 3 days old. Your grade will no longer be recorded.*"
                    
                    for x in submission_track:
                        if (x.submission_id == submission.id):
                            y = x.Mycomment_id
                            break
                        
                    
                    reddit.validate_on_submit = True
                    reddit.comment(y).edit(edited_comment)
                
                    
                
            else:                                           #removes if post is more than  3 days old and in submission_track
                for i in range(len(submission_track)) :                  
                    if(submission_track[i].submission_id == submission.id):
                        remove_comment_id(submission_track[i], track_comments)
                        del submission_track[i]
            
