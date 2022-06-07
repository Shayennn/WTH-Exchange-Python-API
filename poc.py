import os
from pprint import pprint
from dotenv import load_dotenv
from SimpleBitazza import Bitazza


load_dotenv()

obj = Bitazza(
    api_key=os.getenv('API_KEY'),
    user_id=os.getenv('USER_ID'),
    nounce=os.getenv('NOUNCE'),
    signature=os.getenv('SIGNATURE'),
    )

pprint(obj.get_account_info())
pprint(obj.get_account_balance())
