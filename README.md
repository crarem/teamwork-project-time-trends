# Calculating total team time by month logged on all Teamwork.com projects

At my company, we have a large number of projects on the go, all of which are housed in our teamwork.com account which our team logs time to as they work on them. 

Due to the service nature of our business, it is essential for us to understand how much time is being spent on each project to ensure we are a profitable business. 

We have set standalone projects, but sometimes they can run on a monthly basis for years on end, and in such cases we are interested to know on average, how much time is spent per month on these projects. 

Within Teamwork this is difficult to retrieve, reports can only be pulled on one project at a time and for set date ranges. It takes too long and wasn't being looked at. I wanted to build a simple report which showed the project and its time logs for my whole team by month for the last 6 months so that I could get an idea of averages and see any wide oscillations. 

I created these two python scripts to achieve this. 

twtime.py returns all projects from your teamwork.com account and then iterates through each one to return all time entries by month for the last 6 months (and the current month too). It then sends these results to a SQL database which you can reference for reporting as you wish. 

twMonths.py is a script which is referenced in twtime.py for assisting with calulating the end points for the months in the last 6 months of interest. 

You will need to add your teamwork credentials into twtime.py where mentioned, and also will need to set up an SQL database to send the records too. 

Enjoy!
