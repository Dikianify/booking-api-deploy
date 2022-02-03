import psycopg2
import os
from decouple import config
from datetime import date, timedelta

sdate = date(2022,1,1)   # start date
edate = date(2032,1,1)   # end date

dates = [sdate+timedelta(days=x) for x in range((edate-sdate).days)]

weekdays=[]
for date in dates:
  if date.weekday() < 5:
    new_date=date.strftime('%Y-%m-%d')
    weekdays.append(new_date)


con=psycopg2.connect(config('DATABASE_URL'), sslmode='require')

cur=con.cursor()


# cur.execute("CREATE TABLE open_appointments (DATE TEXT PRIMARY KEY NOT NULL, TIME_1 TEXT NOT NULL, TIME_2 TEXT NOT NULL, TIME_3 TEXT NOT NULL, TIME_4 TEXT NOT NULL, TIME_5 TEXT NOT NULL, TIME_6 TEXT NOT NULL);")
# cur.execute("CREATE TABLE booked_appointments (EMAIL TEXT PRIMARY KEY NOT NULL, DATE TEXT NOT NULL, TIME TEXT NOT NULL);")
# con.commit()

for day in weekdays:
  vals = (day, "10:00 - 10:30", "11:00 - 11:30", "1:00 - 1:30", "2:00 - 2:30", "3:00 - 3:30", "4:00 - 4:30")
  cur.execute(f"INSERT INTO open_appointments (DATE, TIME_1, TIME_2, TIME_3, TIME_4, TIME_5, TIME_6) VALUES (%s, %s, %s, %s, %s, %s, %s)", vals)

con.commit()

print(cur.execute('SELECT * FROM open_appointments'))
