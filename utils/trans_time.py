import time


def timestampToTime(timestamp):
    """
    时间戳转日期
    :param timestamp: 时间戳
    :return: 日期
    """
    timeArray = time.localtime(int(timestamp))
    styleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return styleTime


def timeToTimestamp(style_time):
    """
    日期转时间戳
    :param style_time: 日期
    :return: 时间戳
    """
    timeArray = time.strptime(style_time, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


if __name__ == '__main__':
    # print(timestampToTime('1381419600'))
    print(timestampToTime(time.time()))
    print(timeToTimestamp('2013-10-10 23:40:00'))
