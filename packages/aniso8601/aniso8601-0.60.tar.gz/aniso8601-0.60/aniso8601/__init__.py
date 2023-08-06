# -*- coding: utf-8 -*-

#Copyright 2013 Brandon Nielsen
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime

def parse_date(isodatestr):
    #Given a string in any ISO8601 date format, return a datetime.date
    #object that corresponds to the given date. Valid string formats are:
    #
    #Y[YYY]
    #YYYY-MM-DD
    #YYYYMMDD
    #YYYY-MM
    #YYYY-Www
    #YYYYWww
    #YYYY-Www-D
    #YYYYWwwD
    #YYYY-DDD
    #YYYYDDD
    #
    #Note that the ISO8601 date format of ±YYYYY is expressly not supported

    if isodatestr.startswith('+') or isodatestr.startswith('-'):
        raise NotImplementedError('ISO8601 extended year representation not supported.')

    if isodatestr.find('W') != -1:
        #Handle ISO8601 week date format
        return parse_week_date(isodatestr)

    #If the size of the string of 4 or less, assume its a truncated year representation
    if len(isodatestr) <= 4:
        return parse_year(isodatestr)

    datestrsplit = isodatestr.split('-')

    #An ISO string may be a calendar represntation if:
    # 1) When split on a hyphen, the sizes of the parts are 4, 2, 2 or 4, 2
    # 2) There are no hyphens, and the length is 8

    #Check case 1
    if len(datestrsplit) == 2:
        if len(datestrsplit[0]) == 4 and len(datestrsplit[1]) == 2:
            return parse_calendar_date(isodatestr)


    if len(datestrsplit) == 3:
        if len(datestrsplit[0]) == 4 and len(datestrsplit[1]) == 2 and len(datestrsplit[2]) == 2:
            return parse_calendar_date(isodatestr)

    #Check case 2
    if len(isodatestr) == 8 and isodatestr.find('-') == -1:
        return parse_calendar_date(isodatestr)

    #An ISO string may be a ordinal date representation if:
    # 1) When split on a hyphen, the sizes of the parts are 4, 3
    # 2) There are no hyphens, and the length is 7

    #Check case 1
    if len(datestrsplit) == 2:
        if len(datestrsplit[0]) == 4 and len(datestrsplit[1]) == 3:
            return parse_ordinal_date(isodatestr)

    #Check case 2
    if len(isodatestr) == 7 and isodatestr.find('-') == -1:
        return parse_ordinal_date(isodatestr)

    #None of the date representations match
    raise ValueError('String is not an ISO8601 date, perhaps it represents a time or datetime.')

def parse_time(isotimestr):
    #Given a string in any ISO8601 time format, return a datetime.time object
    #that corresponds to the given time. Fixed offset tzdata will be included
    #if UTC offset is given in the input string. Valid time formats are:
    #
    #hh:mm:ss
    #hhmmss
    #hh:mm
    #hhmm
    #hh
    #hh:mm:ssZ
    #hhmmssZ
    #hh:mmZ
    #hhmmZ
    #hhZ
    #hh:mm:ss±hh:mm
    #hhmmss±hh:mm
    #hh:mm±hh:mm
    #hhmm±hh:mm
    #hh±hh:mm
    #hh:mm:ss±hhmm
    #hhmmss±hhmm
    #hh:mm±hhmm
    #hhmm±hhmm
    #hh±hhmm
    #hh:mm:ss±hh
    #hhmmss±hh
    #hh:mm±hh
    #hhmm±hh
    #hh±hh

    #Split the string at the TZ, if necessary
    if isotimestr.find('+') != -1:
        timestr = isotimestr[0:isotimestr.find('+')]
        tzstr = isotimestr[isotimestr.find('+'):]
    elif isotimestr.find('-') != -1:
        timestr = isotimestr[0:isotimestr.find('-')]
        tzstr = isotimestr[isotimestr.find('-'):]
    elif isotimestr.endswith('Z'):
        timestr = isotimestr[:-1]
        tzstr = 'Z'
    else:
        timestr = isotimestr
        tzstr = None

    if tzstr == None:
        return parse_time_naive(timestr)
    elif tzstr == 'Z':
        return parse_time_naive(timestr).replace(tzinfo=UTCOffset('UTC', datetime.timedelta(hours=0)))
    else:
        return parse_time_naive(timestr).replace(tzinfo=parse_timezone(tzstr))

def parse_datetime(isodatetimestr, delimiter='T'):
    #Given a string in ISO8601 date time format, return a datetime.datetime
    #object that corresponds to the given date time.
    #By default, the ISO8601 specified T delimiter is used to split the
    #date and time (<date>T<time>). Fixed offset tzdata will be included
    #if UTC offset is given in the input string.

    isodatestr, isotimestr = isodatetimestr.split(delimiter)

    datepart = parse_date(isodatestr)
    timepart = parse_time(isotimestr)

    return datetime.datetime.combine(datepart, timepart)

def parse_duration(isodurationstr):
    #Given a string representing an ISO 8601 duration, return a
    #datetime.timedelta that matches the given duration. Valid formts are:
    #
    #PnYnMnDTnHnMnS (or any reduced precision equivalent)
    #P<date>T<time>

    if isodurationstr[0] != 'P':
        raise ValueError('String is not a valid ISO8601 duration.')

    #If Y, M, D, H, or S are in the string, assume it is a specified duration
    if isodurationstr.find('Y') != -1 or isodurationstr.find('M') != -1 or isodurationstr.find('D') != -1 or isodurationstr.find('H') != -1 or isodurationstr.find('S') != -1:
        return parse_duration_prescribed(isodurationstr)
    else:
        return parse_duration_combined(isodurationstr)

def parse_interval(isointervalstr, intervaldelimiter='/', datetimedelimiter='T'):
    #Given a string representing an ISO8601 interval, return a
    #tuple of datetime.date or date.datetime objects representing the beginning
    #and end of the specified interval. Valid formats are:
    #
    #<start>/<end>
    #<start>/<duration>
    #<duration>/<end>
    #
    #The <start> and <end> values can represent dates, or datetimes,
    #not times.
    #
    #The format:
    #
    #<duration>
    #
    #Is expressly not supported as there is no way to provide the addtional
    #required context.

    firstpart, secondpart = isointervalstr.split(intervaldelimiter)

    if firstpart[0] == 'P':
        #<duration>/<end>
        #Notice that these are not returned 'in order' (earlier to later), this
        #is to maintain consistency with parsing <start>/<end> durations, as
        #well asmaking repeating interval code cleaner. Users who desire
        #durations to be in order can use the 'sorted' operator.

        #We need to figure out if <end> is a date, or a datetime
        if secondpart.find(datetimedelimiter) != -1:
            #<end> is a datetime
            duration = parse_duration(firstpart)
            enddatetime = parse_datetime(secondpart, delimiter=datetimedelimiter)

            return (enddatetime, enddatetime - duration)
        else:
            #<end> must just be a date
            duration = parse_duration(firstpart)
            enddate = parse_date(secondpart)

            return (enddate, enddate - duration)
    elif secondpart[0] == 'P':
        #<start>/<duration>
        #We need to figure out if <start> is a date, or a datetime
        if firstpart.find(datetimedelimiter) != -1:
            #<end> is a datetime
            duration = parse_duration(secondpart)
            startdatetime = parse_datetime(firstpart, delimiter=datetimedelimiter)

            return (startdatetime, startdatetime + duration)
        else:
            #<start> must just be a date
            duration = parse_duration(secondpart)
            startdate = parse_date(firstpart)

            return (startdate, startdate + duration)
    else:
        #<start>/<end>
        if firstpart.find(datetimedelimiter) != -1 and secondpart.find(datetimedelimiter) != -1:
            #Both parts are datetimes
            return (parse_datetime(firstpart, delimiter=datetimedelimiter), parse_datetime(secondpart, delimiter=datetimedelimiter))
        elif firstpart.find(datetimedelimiter) != -1 and secondpart.find(datetimedelimiter) == -1:
            #First part is a datetime, second part is a date
            return (parse_datetime(firstpart, delimiter=datetimedelimiter), parse_date(secondpart))
        elif firstpart.find(datetimedelimiter) == -1 and secondpart.find(datetimedelimiter) != -1:
            #First part is a date, second part is a datetime
            return (parse_date(firstpart), parse_datetime(secondpart, delimiter=datetimedelimiter))
        else:
            #Both parts are dates
            return (parse_date(firstpart), parse_date(secondpart))

def parse_repeating_interval(isointervalstr, intervaldelimiter='/', datetimedelimiter='T'):
    #Given a string representing an ISO8601 interval repating, return a
    #generator of datetime.date or date.datetime objects representing the
    #dates specified by the repeating interval. Valid formats are:
    #
    #Rnn/<interval>
    #R/<interval>

    if isointervalstr[0] != 'R':
        raise ValueError('String is not a valid ISO8601 repeating interval.')

    #Parse the number of iterations
    iterationpart, intervalpart = isointervalstr.split(intervaldelimiter, 1)

    if len(iterationpart) > 1:
        iterations = int(iterationpart[1:])
    else:
        iterations = None

    interval = parse_interval(intervalpart, intervaldelimiter, datetimedelimiter)

    intervaltimedelta = interval[1] - interval[0]

    #Now, build and return the generator
    if iterations != None:
        return date_generator(interval[0], intervaltimedelta, iterations)
    else:
        return date_generator_unbounded(interval[0], intervaltimedelta)

def parse_year(yearstr):
    #yearstr is of the format Y[YYY]
    #
    #0000 (1 BC) is not representible as a Python date so a ValueError is
    #raised
    #
    #Truncated dates, like '19', refer to 1900-1999 inclusive, we simply parse
    #to 1900-01-01
    #
    #Since no additional resolution is provided, the month is set to 1, and
    #day is set to 1

    if len(yearstr) == 4:
        return datetime.date(int(yearstr), 1, 1)
    else:
        #Shift 0s in from the left to form complete year
        return datetime.date(int(yearstr.ljust(4, '0')), 1, 1)

def parse_calendar_date(datestr):
    #datestr is of the format YYYY-MM-DD, YYYYMMDD, or YYYY-MM
    datestrlen = len(datestr)

    if datestrlen == 10:
        #YYYY-MM-DD
        parseddatetime = datetime.datetime.strptime(datestr, '%Y-%m-%d')

        #Since no 'time' is given, cast to a date
        return parseddatetime.date()
    elif datestrlen == 8:
        #YYYYMMDD
        parseddatetime = datetime.datetime.strptime(datestr, '%Y%m%d')

        #Since no 'time' is given, cast to a date
        return parseddatetime.date()
    elif datestrlen == 7:
        #YYYY-MM
        parseddatetime = datetime.datetime.strptime(datestr, '%Y-%m')

        #Since no 'time' is given, cast to a date
        return parseddatetime.date()
    else:
        raise ValueError('String is not a valid ISO8601 calendar date.')

def parse_week_date(datestr):
    #datestr is of the format YYYY-Www, YYYYWww, YYYY-Www-D, YYYYWwwD
    #
    #W is the week number prefix, ww is the week number, between 1 and 53
    #0 is not a valid week number, which differs from the Python implementation
    #
    #D is the weekday number, between 1 and 7, which differs from the Python
    #implementation which is between 0 and 6

    isoyear = int(datestr[0:4])
    gregorianyearstart = _iso_year_start(isoyear)

    #Week number will be the two characters after the W
    windex = datestr.find('W')
    isoweeknumber = int(datestr[windex + 1:windex + 3])

    if isoweeknumber == 0:
        raise ValueError('00 is not a valid ISO8601 weeknumber.')

    datestrlen = len(datestr)

    if datestr.find('-') != -1:
        if datestrlen == 8:
            #YYYY-Www
            #Suss out the date
            return gregorianyearstart + datetime.timedelta(weeks=isoweeknumber - 1, days=0)
        elif datestrlen == 10:
            #YYYY-Www-D
            isoday = int(datestr[9:10])

            return gregorianyearstart + datetime.timedelta(weeks=isoweeknumber - 1, days=isoday - 1)
        else:
            raise ValueError('String is not a valid ISO8601 week date.')
    else:
        if datestrlen == 7:
            #YYYYWww
            return gregorianyearstart + datetime.timedelta(weeks=isoweeknumber - 1, days=0)
        elif datestrlen == 8:
            #YYYYWwwD
            isoday = int(datestr[7:8])

            return gregorianyearstart + datetime.timedelta(weeks=isoweeknumber - 1, days=isoday - 1)
        else:
            raise ValueError('String is not a valid ISO8601 week date.')

def parse_ordinal_date(datestr):
    #datestr is of the format YYYY-DDD or YYYYDDD
    #DDD can be from 1 - 365, this matches Python's definition

    if datestr.find('-') != -1:
        #YYYY-DDD
        parseddatetime = datetime.datetime.strptime(datestr, '%Y-%j')

        #Since no 'time' is given, cast to a date
        return parseddatetime.date()
    else:
        #YYYYDDD
        parseddatetime = datetime.datetime.strptime(datestr, '%Y%j')

        #Since no 'time' is given, cast to a date
        return parseddatetime.date()

def parse_time_naive(timestr):
    #timestr is of the format hh:mm:ss, hh:mm, hhmmss, hhmm, hh
    #
    #hh is between 0 and 24, 24 is not allowed in the Python time format, since
    #it represents midnight, a time of 00:00:00 is returned
    #
    #mm is between 0 and 60, with 60 used to denote a leap second
    #
    #No tzinfo will be included

    if timestr.count(':') == 2:
        #hh:mm:ss
        timestrarray = timestr.split(':')

        isohour = int(timestrarray[0])
        isominute = int(timestrarray[1])

        if isominute > 60:
            raise ValueError('String is not a valid ISO8601 time.')

        if isohour == 24:
            return datetime.time(hour=0, minute=0)

        #Since the time constructor doesn't handle fractional seconds, we put
        #the seconds in to a timedelta, and add it to the time before returning
        secondsdelta = datetime.timedelta(seconds = float(timestrarray[2]))

        #Now combine todays date (just so we have a date object), the time, the
        #delta, and return the time component
        return (datetime.datetime.combine(datetime.date.today(), datetime.time(hour=isohour, minute=isominute)) + secondsdelta).time()
    elif timestr.count(':') == 1:
        #hh:mm
        timestrarray = timestr.split(':')

        isohour = int(timestrarray[0])
        isominute = float(timestrarray[1]) #Minute may now be a fraction

        if isominute > 60:
            raise ValueError('String is not a valid ISO8601 time.')

        if isohour == 24:
            return datetime.time(hour=0, minute=0)

        #Since the time constructor doesn't handle fractional minutes, we put
        #the minutes in to a timedelta, and add it to the time before returning
        minutesdelta = datetime.timedelta(minutes = isominute)

        #Now combine todays date (just so we have a date object), the time, the
        #delta, and return the time component
        return (datetime.datetime.combine(datetime.date.today(), datetime.time(hour=isohour)) + minutesdelta).time()
    else:
        #Format must be hhmmss, hhmm, or hh
        if timestr.find('.') == -1:
            #No time fractions
            timestrlen = len(timestr)

            if timestrlen == 6:
                #hhmmss
                isohour = int(timestr[0:2])
                isominute = int(timestr[2:4])
                isosecond = int(timestr[4:6])

                if isominute > 60:
                    raise ValueError('String is not a valid ISO8601 time.')

                if isohour == 24:
                    return datetime.time(hour=0, minute=0)

                return datetime.time(hour=isohour, minute=isominute, second=isosecond)
            elif timestrlen == 4:
                #hhmm
                isohour = int(timestr[0:2])
                isominute = int(timestr[2:4])

                if isominute > 60:
                    raise ValueError('String is not a valid ISO8601 time.')

                if isohour == 24:
                    return datetime.time(hour=0, minute=0)

                return datetime.time(hour=isohour, minute=isominute)
            elif timestrlen == 2:
                #hh
                isohour = int(timestr[0:2])

                if isohour == 24:
                    return datetime.time(hour=0)

                return datetime.time(hour=isohour)
            else:
                raise ValueError('String is not a valid ISO8601 time.')
        else:
            #The lowest order element is a fraction
            timestrlen = len(timestr.split('.')[0])

            if timestrlen == 6:
                #hhmmss.
                isohour = int(timestr[0:2])
                isominute = int(timestr[2:4])

                if isominute > 60:
                    raise ValueError('String is not a valid ISO8601 time.')

                if isohour == 24:
                    return datetime.time(hour=0, minute=0)

                #Since the time constructor doesn't handle fractional seconds, we put
                #the seconds in to a timedelta, and add it to the time before returning
                secondsdelta = datetime.timedelta(seconds = float(timestr[4:]))

                #Now combine todays date (just so we have a date object), the time, the
                #delta, and return the time component
                return (datetime.datetime.combine(datetime.date.today(), datetime.time(hour=isohour, minute=isominute)) + secondsdelta).time()
            elif timestrlen == 4:
                #hhmm.
                isohour = int(timestr[0:2])
                isominute = float(timestr[2:])

                if isominute > 60:
                    raise ValueError('String is not a valid ISO8601 time.')

                if isohour == 24:
                    return datetime.time(hour=0, minute=0)

                #Since the time constructor doesn't handle fractional minutes, we put
                #the minutes in to a timedelta, and add it to the time before returning
                minutesdelta = datetime.timedelta(minutes = isominute)

                #Now combine todays date (just so we have a date object), the time, the
                #delta, and return the time component
                return (datetime.datetime.combine(datetime.date.today(), datetime.time(hour=isohour)) + minutesdelta).time()
            elif timestrlen == 2:
                #hh.
                isohour = float(timestr)

                if isohour == 24:
                    return datetime.time(hour=0, minute=0)

                #Since the time constructor doesn't handle fractional hours, we put
                #the hours in to a timedelta, and add it to the time before returning
                hoursdelta = datetime.timedelta(hours = isohour)

                #Now combine todays date (just so we have a date object), the time, the
                #delta, and return the time component
                return (datetime.datetime.combine(datetime.date.today(), datetime.time(hour=0)) + hoursdelta).time()

def parse_timezone(tzstr):
    #tzstr can be ±hh:mm, ±hhmm, ±hh, the Z case is handled elsewhere

    tzstrlen = len(tzstr)

    if tzstrlen == 6:
        #±hh:mm
        tzhour = int(tzstr[1:3])
        tzminute = int(tzstr[4:6])

        if tzstr[0] == '+':
            return UTCOffset(tzstr, datetime.timedelta(hours=tzhour, minutes=tzminute))
        else:
            if tzhour == 0 and tzminute == 0:
                raise ValueError('String is not a valid ISO8601 time offset.')
            else:
                return UTCOffset(tzstr, -datetime.timedelta(hours=tzhour, minutes=tzminute))
    elif tzstrlen == 5:
        #±hhmm
        tzhour = int(tzstr[1:3])
        tzminute = int(tzstr[3:5])

        if tzstr[0] == '+':
            return UTCOffset(tzstr, datetime.timedelta(hours=tzhour, minutes=tzminute))
        else:
            if tzhour == 0 and tzminute == 0:
                raise ValueError('String is not a valid ISO8601 time offset.')
            else:
                return UTCOffset(tzstr, -datetime.timedelta(hours=tzhour, minutes=tzminute))
    elif tzstrlen == 3:
        #±hh
        tzhour = int(tzstr[1:3])

        if tzstr[0] == '+':
            return UTCOffset(tzstr, datetime.timedelta(hours=tzhour))
        else:
            if tzhour == 0:
                raise ValueError('String is not a valid ISO8601 time offset.')
            else:
                return UTCOffset(tzstr, -datetime.timedelta(hours=tzhour))
    else:
        raise ValueError('String is not a valid ISO8601 time offset.')

def parse_duration_prescribed(durationstr):
    #durationstr can be of the form PnYnMnDTnHnMnS

    #Make sure only the lowest order element has decimal precision
    if durationstr.count('.') > 1:
        raise ValueError('String is not a valid ISO8601 duration.')
    elif durationstr.count('.') == 1:
        #There should only ever be 1 letter after a decimal if there is more
        #then one, the string is invalid
        lettercount = 0;

        for character in durationstr.split('.')[1]:
            if character.isalpha() == True:
                lettercount += 1

            if lettercount > 1:
                raise ValueError('String is not a valid ISO8601 duration.')

    #Parse the elements of the duration
    if durationstr.find('T') == -1:
        if durationstr.find('Y') != -1:
            years = _parse_duration_element(durationstr, 'Y')
        else:
            years = 0

        if durationstr.find('M') != -1:
            months = _parse_duration_element(durationstr, 'M')
        else:
            months = 0

        if durationstr.find('D') != -1:
            days = _parse_duration_element(durationstr, 'D')
        else:
            days = 0

        #No hours, minutes or seconds
        hours = 0
        minutes = 0
        seconds = 0
    else:
        firsthalf = durationstr[:durationstr.find('T')]
        secondhalf = durationstr[durationstr.find('T'):]

        if  firsthalf.find('Y') != -1:
            years = _parse_duration_element(firsthalf, 'Y')
        else:
            years = 0

        if firsthalf.find('M') != -1:
            months = _parse_duration_element(firsthalf, 'M')
        else:
            months = 0

        if firsthalf.find('D') != -1:
            days = _parse_duration_element(firsthalf, 'D')
        else:
            days = 0

        if secondhalf.find('H') != -1:
            hours = _parse_duration_element(secondhalf, 'H')
        else:
            hours = 0

        if secondhalf.find('M') != -1:
            minutes = _parse_duration_element(secondhalf, 'M')
        else:
            minutes = 0

        if secondhalf.find('S') != -1:
            seconds = _parse_duration_element(secondhalf, 'S')
        else:
            seconds = 0

    totaldays = years * 365 + months * 30 + days

    return datetime.timedelta(days=totaldays, hours=hours, minutes=minutes, seconds=seconds)

def parse_duration_combined(durationstr):
    #Period of the form P<date>T<time>

    #Split the string in to its component parts
    datepart, timepart = durationstr[1:].split('T') #We skip the 'P'

    datevalue = parse_date(datepart)
    timevalue = parse_time(timepart)

    totaldays = datevalue.year * 365 + datevalue.month * 30 + datevalue.day

    return datetime.timedelta(days=totaldays, hours=timevalue.hour, minutes=timevalue.minute, seconds=timevalue.second, microseconds=timevalue.microsecond)

def _parse_duration_element(durationstr, elementstr):
    #Extracts the specified portion of a duration, for instance, given:
    #durationstr = 'T4H5M6.1234S'
    #elementstr = 'H'
    #
    #returns 4
    #
    #Note that the string must start with a character, so its assumed the
    #full duration string would be split at the 'T'

    durationstartindex = 0
    durationendindex = durationstr.find(elementstr)

    for characterindex in xrange(durationendindex - 1, 0, -1):
        if durationstr[characterindex].isalpha() == True:
            durationstartindex = characterindex
            break

    durationstartindex += 1

    return float(durationstr[durationstartindex:durationendindex])

def _iso_year_start(isoyear):
    #Given an ISO year, returns the equivalent of the start of the year on the
    #Gregorian calendar (which is used by Python)
    #Stolen from:
    #http://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar

    #Determine the location of the 4th of January, the first week of the ISO
    #year in the week containing the 4th of January
    #http://en.wikipedia.org/wiki/ISO_week_date
    fourth_jan = datetime.date(isoyear, 1, 4)

    #Note the conversion from ISO day (1 - 7) and Python day (0 - 6)
    delta = datetime.timedelta(fourth_jan.isoweekday() - 1)

    #Return the start of the year
    return fourth_jan - delta

def date_generator(startdate, timedelta, iterations):
    currentdate = startdate
    currentiteration = 0

    while currentiteration < iterations:
        yield currentdate

        #Update the values
        currentdate += timedelta
        currentiteration += 1

def date_generator_unbounded(startdate, timedelta):
    currentdate = startdate

    while True:
        yield currentdate

        #Update the value
        currentdate += timedelta

class UTCOffset(datetime.tzinfo):
    def __init__(self, name, utcdelta):
        self._name = name
        self._utcdelta = utcdelta

    def utcoffset(self, dt):
        return self._utcdelta

    def tzname(self, dt):
        return self._name

    def dst(self, dt):
        #ISO8601 specifies offsets should be different if DST is required,
        #instead of allowing for a DST to be specified
        return None
