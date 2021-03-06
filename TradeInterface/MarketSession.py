import pytz
import datetime

market_sessions = [[datetime.time(7, 00), datetime.time(9, 30), 'EXTENDED'],
                   [datetime.time(9, 30), datetime.time(16, 00), 'REGULAR'],
                   [datetime.time(16, 00), datetime.time(20, 00), 'EXTENDED']]


#
#
#
def market_session() -> str:
    eastern_time_now = current_time()

    for i in range(len(market_sessions)):
        if market_sessions[i][0] < eastern_time_now.time() <= market_sessions[i][1]:
            return market_sessions[i][2]

    return 'NO_TRADE'


#
#
#
def next_session() -> datetime.datetime:
    eastern_time_now = current_time()

    session_idx = None
    for i in range(len(market_sessions)):
        if market_sessions[i][0] < eastern_time_now.time() <= market_sessions[i][1]:
            session_idx = i

    # increase session_idx
    if session_idx is None:
        next_session_idx = 0
    else:
        next_session_idx = (session_idx + 1) % len(market_sessions)

    #
    if eastern_time_now.time() > market_sessions[next_session_idx][0]:
        eastern_time_now = eastern_time_now + datetime.timedelta(days=1)

    return eastern_time_now.replace(hour=market_sessions[next_session_idx][0].hour, minute=market_sessions[next_session_idx][0].minute, second=0)


#
#
#
def datetime_delay(hours=0, minutes=0, seconds=0):
    return current_time() + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)


#
#
#
def current_time():
    return datetime.datetime.now(pytz.timezone('US/Eastern'))
