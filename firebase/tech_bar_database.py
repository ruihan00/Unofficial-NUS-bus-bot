from firebase.managedb import db
from enum import Enum
from datetime import datetime, timedelta

collection_ref = db.collection('tech_bar')
subscription_ref = collection_ref.document('members').collection('users')
datetime_format = "%d/%m/%Y"

class StatusCodes(Enum):
    OK = 200
    USER_EXISTS = 401
    USER_DOES_NOT_EXIST = 402
    SERVER_ERROR = 500

def parse_datetime(string):
    sgt_offset = timedelta(hours=8)

    # Get the current time in UTC
    current_time_utc = datetime.strptime(string, datetime_format)

    # Calculate the current time in Singapore Time
    current_time_sgt = current_time_utc + sgt_offset
    return current_time_sgt
def add_user(first_name, last_name, username, userid):
    try:
        user_ref = subscription_ref.document(str(userid))
        doc = user_ref.get()
        if doc.exists:
            return StatusCodes.USER_EXISTS
        user_ref.set(
            {
                'first_name': first_name,
                'last_name': last_name,
                'userid': userid,
                'quarantine_date': None,
                'username': username,
                'last_login': datetime.now().strftime(datetime_format),
                'login_streak': 0,
                'days_since_last_quarantine': 0
            }
        )
        return StatusCodes.OK
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR


def remove_user(userid):
    try:
        user_ref = subscription_ref.document(str(userid))
        doc = user_ref.get()
        if not doc.exists:
            return StatusCodes.USER_DOES_NOT_EXIST
        user_ref.delete()
        return StatusCodes.OK
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR


def get_all_users():
    try:
        docs = subscription_ref.get()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR


def extend_user_quarantine_date(userid):
    try:
        user_ref = subscription_ref.document(str(userid))
        doc = user_ref.get()
        if not doc.exists:
            return StatusCodes.USER_DOES_NOT_EXIST
        quarantine_date = datetime.now() + timedelta(days=5)
        user_ref.update(
            {
                'quarantine_date': quarantine_date.strftime(datetime_format)
            }
        )
        update_user_last_login(userid)
        return StatusCodes.OK
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR

def quarantine_predicate(user):
    quarantine_date = datetime.now() + timedelta(days=1)
    user_quarantine_date = user['quarantine_date']
    if not user_quarantine_date:
        return False
    user_quarantine_date = parse_datetime(user_quarantine_date)
    return user_quarantine_date < quarantine_date

def get_quarantined_users():
    try:
        # Find users whose quarantine date is before the current date
        docs = subscription_ref.get()
        users = [doc.to_dict() for doc in docs]
        return list(filter(quarantine_predicate, users))
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR


def at_risk_predicate(user):
    at_risk_date = datetime.now() + timedelta(days=2)
    user_quarantine_date = user['quarantine_date']
    if not user_quarantine_date:
        return True
    user_quarantine_date = parse_datetime(user_quarantine_date)
    return datetime.now() < user_quarantine_date < at_risk_date


def get_at_risk_users():
    try:
        docs = subscription_ref.get()
        users = [doc.to_dict() for doc in docs]
        return list(filter(at_risk_predicate, users))
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR

def update_users_days_since_last_quarantine():
    try:
        users_ref = subscription_ref.get()
        for user in users_ref:
            user = user.to_dict()
            if user['quarantine_date'] is None or parse_datetime(user['quarantine_date']) < datetime.now() + timedelta(days=1):
                return StatusCodes.OK
            subscription_ref.document(user['userid']).update(
                {
                    'days_since_last_quarantine': user['days_since_last_quarantine'] + 1
                }
            )
        return StatusCodes.OK
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR

def update_user_last_login(userid):
    try:
        user_ref = subscription_ref.document(str(userid))
        doc = user_ref.get()
        if not doc.exists:
            return StatusCodes.USER_DOES_NOT_EXIST
        if (parse_datetime(doc.to_dict()['last_login']) - datetime.now()).days == -1:
            user_ref.update(
                {
                    'login_streak': doc.to_dict()['login_streak'] + 1,
                    'last_login': datetime.now().strftime(datetime_format)

                }
            )
        else :
            user_ref.update(
                {
                    'last_login': datetime.now().strftime(datetime_format)
                }
            )
        
        return StatusCodes.OK
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR

print(get_quarantined_users())