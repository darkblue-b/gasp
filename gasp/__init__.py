"""
GASP Python Package
"""

"""
Compress files with Python
"""


def tar_compress_folder(tar_fld, tar_file):
    """
    Compress a given folder
    """
    
    from gasp import exec_cmd
    
    cmd = 'cd {p} && tar -czvf {tar_f} {fld}'.format(
        tar_f=tar_file, fld=str(os.path.basename(tar_fld)),
        p=str(os.path.dirname(tar_fld))
    )
    
    code, out, err = exec_cmd(cmd)
    
    return tar_file


def zip_files(lst_files, zip_file):
    """
    Zip all files in the lst_files
    """
    
    import zipfile
    import os
    
    __zip = zipfile.ZipFile(zip_file, mode='w')
    
    for f in lst_files:
        __zip.write(f, os.path.relpath(f, os.path.dirname(zip_file)),
                       compress_type=zipfile.ZIP_DEFLATED)
    
    __zip.close()


def zip_folder(folder, zip_file):
    from gasp.oss import list_files
    
    files = list_files(folder)
    
    zip_files(files, zip_file)


"""
Datetime Objects Management
"""


def day_to_intervals(interval_period):
    """
    Divide a day in intervals with a duration equal to interval_period
    
    return [
        ((lowerHour, lowerMinutes), (upperHour, upperMinutes)),
        ((lowerHour, lowerMinutes), (upperHour, upperMinutes)),
        ...
    ]
    """
    
    import datetime
    
    MINUTES_FOR_DAY = 24 * 60
    NUMBER_INTERVALS = MINUTES_FOR_DAY / interval_period
    
    hour = 0
    minutes = 0
    INTERVALS = []
    
    for i in range(NUMBER_INTERVALS):
        __minutes = minutes + interval_period
        __interval = (
            (hour, minutes),
            (hour + 1 if __minutes >= 60 else hour,
             0 if __minutes == 60 else __minutes - 60 if __minutes > 60 else __minutes)
        )
        
        INTERVALS.append(__interval)
        minutes += interval_period
        
        if minutes == 60:
            minutes = 0
            hour += 1
        
        elif minutes > 60:
            minutes = minutes - 60
            hour += 1
    
    return INTERVALS


def day_to_intervals2(intervaltime):
    """
    Divide a day in intervals with a duration equal to interval_period
    
    intervaltime = "01:00:00"
    
    return [
        ('00:00:00', '01:00:00'), ('01:00:00', '02:00:00'),
        ('02:00:00', '03:00:00'), ...,
        ('22:00:00', '23:00:00'), ('23:00:00', '23:59:00')
    ]
    """
    
    from datetime import datetime, timedelta
    
    TIME_OF_DAY = timedelta(hours=23, minutes=59, seconds=59)
    DURATION    = datetime.strptime(intervaltime, "%H:%M:%S")
    DURATION    = timedelta(
        hours=DURATION.hour, minutes=DURATION.minute,
        seconds=DURATION.second
    )
    
    PERIODS = []
    
    upperInt = timedelta(hours=0, minutes=0, seconds=0)
    
    while upperInt < TIME_OF_DAY:
        if not PERIODS:
            lowerInt = timedelta(hours=0, minutes=0, seconds=0)
        
        else:
            lowerInt = upperInt
        
        upperInt = lowerInt + DURATION
        
        PERIODS.append((
            "0" + str(lowerInt) if len(str(lowerInt)) == 7 else str(lowerInt),
            "0" + str(upperInt) if len(str(upperInt)) == 7 else str(upperInt)
        ))
    
    PERIODS[-1] = (PERIODS[-1][0], '23:59:59')
    
    return PERIODS


"""
Encripting strings
"""
def str_to_ascii(__str):
    """
    String to numeric code
    """
    
    return ''.join(str(ord(c)) for c in __str)


def id_encodefile(file__):
    """
    Find encoding of file using chardet
    """
    
    from chardet.universaldetector import UniversalDetector
    
    detector = UniversalDetector()
    
    for l in open(file__):
        detector.feed(l)
        
        if detector.done:
            break
    
    detector.close()
    
    return detector.result['encoding']


"""
Numbers utils
"""

def __round(n, n_digits):
    """
    Round n
    """
    
    dp = str(n).split('.')[1]
    
    mnt = str(int(dp[:n_digits]) + 1) if int(dp[n_digits]) >= 5 else dp[:n_digits]
    
    return int(n) + float('0.{}'.format(mnt))

