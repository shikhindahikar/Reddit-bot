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

grade_types = {'PO01':1, 'FR02':2, 'AG03':3, 'G04':4, 'G06':6, 'VG08':8, 'VG10':10, 'F12':12, 'F15':15, 'VF20':20, 'VF25':25, 'VF35':35, 'VF30':30, 'XF40':40, 'XF45':45, 'AU50':50, 'AU53':53, 'AU55':55, 'AU58':58, 'MS60':60, 'MS61':61, 'MS62':62, 'MS63':63, 'MS64':64, 'MS65':65, 'MS66':66, 'MS67':67, 'MS68':68, 'MS69':69, 'MS70':70, 'PO':1, 'Poor':1, 'FR':2, 'AG':3, 'G':4, 'Good':4, 'VG':8, 'F':12, 'Fine':12, 'VF':20, 'XF':40, 'AU':50,'BU':60, 'MS':60}

reddit = praw.Reddit(user_agent="CoinGrade bot 0.1",
                     client_id="ik7ILQHFETC7QQ", client_secret="8fMRTIFaxMVOnXsUng94OYMkQdA",
                     username="coin_grader_bot", password="yitzchokrcgbot")

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

def check_metric(metric, grade):
    for x in metric:
        if(x in grade):
            return True
    
    return False
    
submission_track = []       #tracks submissions which have been replied to and are less than or 3 days old
grade_list = []             #contains grades of different comments
    
while(True):
    
    for submission in subreddit.new():
        
        if(submission.title == 'Coin grading test'):             #temporary if statement for testing
            
            
            converted_submission_dt = datetime.datetime.utcfromtimestamp(submission.created_utc)
            current_time_utc = datetime.datetime.utcnow()
            
            date_difference = current_time_utc - converted_submission_dt
            
            in_list = False
            
            if(date_difference.days <= 3):
                for old_submission in submission_track :           #check if this post has already been checked by bot
                    
                    if(old_submission.submission_id == submission.id):
                        in_list = True
                        break
                
                if(not in_list):
                    mycomment = submission.reply("Hi, I am coin grading bot!" + "\n\n" + "*This comment will be edited every 5 minutes to update average grade*")
                    comment_id = mycomment.id
                    obj = sub_track(submission.id, comment_id)              #creating objects for  tracking
                    submission_track.append(obj)
                    
                    
                metric_list = []
                
                for comment in submission.comments:
                    if (comment.score >= 0 and  comment.id not in track_comments or comment.edited):
                        curr_comment = comment.body
                        metric_list.append(re.findall(r'\[(.*?)\]', curr_comment))
                        metric_list = [x for x in metric_list if x]
                        track_comments.append(comment.id)
                
                for metric in metric_list:
                    for x in metric:
                        grade_list.append(x.strip('\\'))
                
                
                numeric_grade = []
                
                for grade in grade_list:
                    if(check_metric(grade, grade_types) ):
                        numeric_grade.append(grade_types[grade])
                    else:
                        grade_list.remove(grade)
                
                if(grade_list and numeric_grade):                             #control block which edits comment
                    average = int(mean(numeric_grade))
                    final_avg = search_avg_grade(average)                 #finds the correspoding key in grade_types
                    edited_comment = mycomment.body + "\n This is the average: " + final_avg
                
                    for x in submission_track:
                        if (x.submission_id == submission.id):
                            y = x.Mycomment_id
                            break
                        
                    del grade_list[:]
                    del numeric_grade[:]
                    
                    reddit.validate_on_submit = True
                    reddit.comment(y).edit(edited_comment)
                
                
            else:                                           #removes if post is more than  3 days old and in submission_track
                for i in range(len(submission_track)) :                  
                    if(submission_track[i].submission_id == submission.id):
                        remove_comment_id(submission_track[i], track_comments)
                        del submission_track[i]
            