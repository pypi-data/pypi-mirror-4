from DateTime import DateTime
from types import ListType, TupleType


def getNoSecDate(date):
    return date - float(date.millis()%60000) / (24*3600*1000)

def splitJob(job):
    splitted = job.split()
    schedule = splitted[:4]
    schedule = [part.find(',') != -1 and part.split(',') or part for part in schedule]
    expression = ' '.join(splitted[4:])
    return dict(schedule = schedule,
                expression = expression)

def getNextScheduledExecutionTime(schedule, current_date):
    # Return the date at which the task was last scheduled
    # Input: current_date
    # Output: The earlies date after the current date at which the task should be executed

    scheduled_minute, scheduled_hour, scheduled_day_of_month, scheduled_month = schedule

    current_date = getNoSecDate(current_date)

    c_year, c_month, c_day, c_hour, c_minute, c_seconds, c_zone = current_date.parts()

    # Minute
    if scheduled_minute == '*':
        next_minute = c_minute
    else:
        if type(scheduled_minute) in (ListType, TupleType):
            next_minute = int(scheduled_minute[0])
            for min in scheduled_minute:
                #Convert this from string to int to ensure comparison works
                min_int = int(min)
                if min_int >= c_minute:
                    next_minute = min_int
                    break
        else:
            next_minute = int(scheduled_minute)

    # Hour
    if scheduled_hour == '*':
        next_hour = c_hour
    else:
        if type(scheduled_hour) in (ListType, TupleType):
            next_hour = int(scheduled_hour[0])
            for hour in scheduled_hour:
                #Convert this from string to int to ensure comparison works
                hour_int = int(hour)
                if hour_int >= c_hour:
                    if (c_hour, c_minute) <= (hour_int, next_minute):
                        next_hour = hour_int
                        break
        else:
            next_hour = int(scheduled_hour)

    # Increase hour if necessary
    if scheduled_hour == '*':
        if (c_hour, c_minute) > (next_hour, next_minute):
            next_hour = c_hour + 1
            if next_hour > 23:
                next_hour = 0

    # Day of month
    if scheduled_day_of_month == '*':
        next_day=c_day
    else:
        if type(scheduled_day_of_month) in (ListType, TupleType):
            next_day = int(scheduled_day_of_month[0])
            for day in scheduled_day_of_month:
                #Convert this from string to int to ensure comparison works
                day_int = int(day)
                if day_int >= c_day:
                    if (c_day, c_hour, c_minute) <= (day_int, next_hour, next_minute):
                        next_day = day_int
                        break
        else:
            next_day = int(scheduled_day_of_month)

    # Increase day of month if necessary
    if scheduled_day_of_month == '*':
        if (c_day, c_hour, c_minute) > (next_day, next_hour, next_minute):
            next_day = c_day + 1
            if c_month in (1, 3, 5, 7, 8, 10, 12) and next_day > 31:
                next_day = 1
            elif c_month in (4, 6, 9, 11) and next_day > 30:
                next_day = 1
            elif  c_month == 2:
                is_leap_year = DateTime(c_year, c_month, c_day).isLeapYear()
                if (is_leap_year and next_day > 29) or \
                   (not is_leap_year and next_day > 28):
                    next_day = 1

    # Month
    if scheduled_month == '*':
        next_month = c_month
    else:
        if type(scheduled_month) in (ListType, TupleType):
            next_month = int(scheduled_month[0])
            for month in scheduled_month:
                #Convert this from string to int to ensure comparison works
                month_int = int(month)
                if month_int >= c_month:
                    if (c_month, c_day, c_hour, c_minute) <= (month_int, next_day, next_hour, next_minute):
                        next_month = month_int
                        break
        else:
            next_month = int(scheduled_month)

    # Increase month if necessary
    if scheduled_month == '*':
        if (c_month, c_day, c_hour, c_minute) > (next_month, next_day, next_hour, next_minute):
            next_month = next_month + 1
            if next_month > 12:
                next_month = 1

    # Year
    next_year = c_year

    # Increase year if necessary
    if (c_year, c_month, c_day, c_hour, c_minute) > (next_year, next_month, next_day, next_hour, next_minute):
        next_year += 1

    # some more sanity stuff added by Huub:
    if next_month != c_month:
        if scheduled_day_of_month == "*":
            next_day = 1
        if scheduled_minute == "*":
            next_minute = 0
        if scheduled_hour == "*":
            next_hour = 0

        if type(scheduled_day_of_month) in (ListType, TupleType):
            next_day = int(scheduled_day_of_month[0])
        if type(scheduled_minute) in (ListType, TupleType):
            next_minute = int(scheduled_minute[0])
        if type(scheduled_hour) in (ListType, TupleType):
            next_hour = int(scheduled_hour[0])

    if next_day != c_day:
        if scheduled_minute == "*":
            next_minute = 0
        if scheduled_hour == "*":
            next_hour = 0

        if type(scheduled_minute) in (ListType, TupleType):
            next_minute = int(scheduled_minute[0])
        if type(scheduled_hour) in (ListType, TupleType):
            next_hour = int(scheduled_hour[0])


    if next_hour != c_hour:
        if scheduled_minute == "*":
            next_minute = 0

        if type(scheduled_minute) in (ListType, TupleType):
            next_minute = int(scheduled_minute[0])


    date_string = "%d/%02d/%02d %02d:%02d %s" % (next_year, next_month, next_day, next_hour, next_minute, c_zone)


    try:
        return DateTime(date_string)
    except DateTime.DateError:
        return DateTime('2500/12/31 00:00')


def isPending(schedule, last_executed_time, now = None):
    """ Return 1 if task is pending, 0 else

    If the task was already run in this intervall, do nothing
    Otherwise run the task if the current date falls in this intervall
    """
    if now is None:
        now = getNoSecDate(DateTime())
    pending = False

    current_next_scheduled = getNextScheduledExecutionTime(schedule, now)
    last_next_scheduled = getNextScheduledExecutionTime(schedule, last_executed_time)

    if last_next_scheduled < current_next_scheduled:
        if last_next_scheduled <= now:
            pending = True

    elif last_next_scheduled == current_next_scheduled:
        # Was already executed for this schedule
        pending = False

    elif last_next_scheduled > current_next_scheduled:
        # Bad initialization date ?
        pending = False

    return pending


def _main():
    # Main program for testing.
    sched = [ '*', '*', '*', '*' ]
    lext  = DateTime("2010/10/31 02:59:12 GMT+2")
    curr  = DateTime("2010/10/31 02:00:12 GMT+1")
    next  = getNextScheduledExecutionTime(sched, curr)
    bpend = isPending(sched, lext, curr)
    print "getNoSecDate(%s) = %s" % (str(curr), str(getNoSecDate(curr)))
    print "%s -> %s" %(str(curr), str(next))
    print "%s = isPending(%s, %s)" %(str(bpend), str(sched), str(curr))

if __name__ == "__main__":
    _main()
