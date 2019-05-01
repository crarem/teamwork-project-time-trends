#!/user/bin/env python

import datetime
from datetime import datetime
from datetime import timedelta
from time import strptime
import json

def last_day_of_month(day):										#defining function named last_day_of_month on specific date

    next_month = day.replace(day=28) + timedelta(days=4)			#Adding four days to the 28th day always takes you to next month
    date =  next_month - timedelta(days=next_month.day)			#Subtracting the number of days into next month that were returned above to get last day of specified date's month
    date = date.strftime('%Y%m%d')								#Transforming this into a format suitable for the Teamwork projects API
    return date													
