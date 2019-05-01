#!/user/bin/env python

import time
import requests
from requests.auth import HTTPBasicAuth
import datetime
import MySQLdb
from datetime import timedelta
from twMonths import last_day_of_month 										#Secondary script created to help return end of month dates

#setting up teamwork projects connection parameters

Url = 'https://<subdomain>.teamwork.com/projects.json'
un = '<username>'
pw = '<pasword>'
headers = {'content-length':'0'}

#setting up project ID array

r1 = requests.get(Url,headers=headers,auth=HTTPBasicAuth(un,pw))				#pulling in all projects from teamwork account
print('Initiating Teamwork requests...')
data = r1.json()
numProjects = len(data['projects'])											#counting the number of projects returned
pj = []																		#setting empty arrays for project ID, company and name
pjName = []
pjCompany = []

for x in range(0, numProjects-1):											#iterating over each project and populating arrays
    pid = data['projects'][x]['id']
    pj_name = data['projects'][x]['name']
    pj_company = data['projects'][x]['company']['name']
    pj.append(pid)
    pjName.append(pj_name)
    pjCompany.append(pj_company)

#Setting up month start and end arrays

cur_year = int(datetime.datetime.now().strftime("%Y"))						#Setting year we are currently in
cur_month = int(datetime.datetime.now().strftime("%m"))						#Setting the month we are currently in
prev_year = cur_year-1														#Setting last year
mo_end1 = []																	#Setting up empty arrays for start and end of month dates
mo_end2 = []
mo_start1 = []
mo_start2 = []

#iterating down from current month to beginning of this year month by month

for month in range(cur_month,0,-1):
    res = last_day_of_month(datetime.date(cur_year,month,1))					#finding the last day of month in question using the prebuilt function
    mo_end1.append(res)														#adding this to the month end array for this year
    res2 = datetime.date(cur_year,month,1).strftime('%Y%m%d')				#the first day of the month in question
    mo_start1.append(res2)													#adding this to the month start array for this year

#iterating through full 12 months of last year

for month in range(12,0,-1):
    res = last_day_of_month(datetime.date(prev_year,month,1))				#finding the last day of the previous year month in question using the prebuilt function
    mo_end2.append(res)														#adding this to the month end array for last year
    res2 = datetime.date(prev_year,month,1).strftime('%Y%m%d')				#returning the first day of the previous year month in question
    mo_start2.append(res2)													#adding this to the month start array for last year


month_ends =  mo_end1 + mo_end2												#Creating an array of all month end dates
month_ends = month_ends[0:7]													#Grabbing the most recent 7 months (includes this month)
month_starts = mo_start1 + mo_start2											#Creating an array of all month start dates
month_starts = month_starts[0:7]												#Grabbing the most recent 7 months (includes this month)

#running time entry requests for each project over 6 months and summing results
#setting teamwork request URLs to bring in time entries using the dateranges calculated above (will use concatenation)

Url2a = 'https://<subdomain>.teamwork.com/projects/'
Url2b = '/time_entries.json?fromdate='
Url2c = '&todate='

time_matrix = []																 					 #setting empty time matrix before looping

for y in range(0,numProjects-1):        										 					 #setting iteration length to number of projects in account
    sixMoTime_totals=[]														 				     #setting empty array for project's 6 month time totals
    sixMoTime_totals.append(pjCompany[y])									 					 #starting the array with company, project name and project ID entries
    sixMoTime_totals.append(pjName[y])
    sixMoTime_totals.append(pj[y])
    for m in range(0,len(month_ends)):															 #starting loop over most recent 7 months (including this month)
        Url2 = Url2a + str(pj[y]) + Url2b + str(month_starts[m]) + Url2c + str(month_ends[m])    #contanating to build teamwork request URL with start and end dates
        
        moTime = requests.get(Url2,headers=headers,auth=HTTPBasicAuth(un,pw)).json()				 #making teamwork request using the newly built URL
        
        timeLen = len(moTime['time-entries'])													 #Seeing how many time entries are present for the month
        
        if timeLen == 0:																			 #Handling case where there are no time entries in a given month for a project
            sixMoTime_totals.append(0)
            
        else:
            month_dur=[]																			 #Setting empty total month time array for capturing month time total in following loop
            for z in range(0,timeLen):															 #Looping over the number of time entries for the month
                moTime_hours = int(moTime['time-entries'][z]['hours'])							 #Finding the number of hours logged for the z'th entry
                moTime_hmins = moTime_hours*60													 #Converting this into minutes
                moTime_minutes = int(moTime['time-entries'][z]['minutes'])						 #Finding the number of minutes logged (on top of the hours logged i.e. 1h 26mins, this returns 26mins)

                month_dur.append( moTime_hmins+moTime_minutes)									 #Adding together the hours (in mins) and minutes to form total minutes logged for this time entry
            
            month_total = sum(month_dur)															 #After all time entries have been iterated over, this sums all entries into total time in mins for the month
            
            sixMoTime_totals.append(month_total)													 #Appends that month to the six month time array
    
    time_matrix.append(sixMoTime_totals)															 #Once all months have been checked, this project has been populated with its company, name, id and time per month, it is added to the master matrix now
    print 'Last six months mins for project ',pj[y],'was ',sixMoTime_totals						 #Printing to the user what the result was for this project for feedback


#Exporting the time matrix to SQL database for access by dashboard reporting

#Setting SQL database parameters for connection

db = MySQLdb.connect(host='<hostIP>',user='<username>',passwd='<user_pwd>',db='<database>')

cur = db.cursor()

resetQuery = "DELETE FROM entries"						#clearing the database before repopulation
cur.execute(resetQuery)
db.commit()												
print("SQL database reset!")								#commiting and printing reset complete


#setting up query for populating the 6 month time entries per project
query = "REPLACE INTO entries(company, project,projectid, m0,m1,m2,m3,m4,m5,m6,entryid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

#iterating over each project 6mo time entry and executing the SQL query with these values
for s in range (0,numProjects-1):     #set to numProjects-1
    values = (time_matrix[s][0],time_matrix[s][1],time_matrix[s][2],time_matrix[s][3],time_matrix[s][4],time_matrix[s][5],time_matrix[s][6],time_matrix[s][7],time_matrix[s][8],time_matrix[s][9],s+1)
    cur.execute(query,values)

db.commit()
print("SQL database updated!")							#commiting to database and printing update complete

cur.execute("SELECT * FROM entries")						#returning all entries for sanity check

#for row in cur.fetchall():
    #print row[:]

db.close()												#closing database connection

