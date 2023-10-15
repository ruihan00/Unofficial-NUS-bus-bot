from firebase.managedb import db
from enum import Enum
collection_ref = db.collection('affirmations_bot')
subscription_ref = collection_ref.document('subscription').collection('users')

class StatusCodes(Enum):
    OK = 200
    USER_EXISTS = 401
    USER_DOES_NOT_EXIST = 402
    SERVER_ERROR = 500


def add_subscriber(first_name, last_name, chatid):
    try:
        user_ref = subscription_ref.document(str(chatid))
        doc = user_ref.get()
        if doc.exists:
            return StatusCodes.USER_EXISTS
        user_ref.set(
            {
                'first_name': first_name,
                'last_name': last_name,
                'chatid': chatid
            }
        )
        return StatusCodes.OK
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR

def remove_subscriber(chatid):
    try:
        user_ref = subscription_ref.document(str(chatid))
        doc = user_ref.get()
        if not doc.exists:
            return StatusCodes.USER_DOES_NOT_EXIST
        user_ref.delete()
        return StatusCodes.OK
    except Exception as e:
        print(e)
        return StatusCodes.SERVER_ERROR

def get_all_subscribers():
    try:
        docs = subscription_ref.stream()
        subscribers = []
        for doc in docs:
            subscribers.append(
                doc.to_dict()
            )
        return subscribers
    except Exception as e:
        return StatusCodes.SERVER_ERROR

