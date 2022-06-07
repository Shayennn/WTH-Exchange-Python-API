import json
from websocket import create_connection


class MessageType:
    REQUEST = 0
    REPLY = 1
    SUBSCRIBE_TO_EVENT = 2
    EVENT = 3
    UNSUBSCRIBE_FROM_EVENT = 4
    ERROR = 5

ERROR_CODE = {
    20: "Not Authorized",
    100: "Invalid Response",
    101: "Operation Failed",
    102: "Server Error",
    104: "Resource Not Found",
}

class BitazzaException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'BitazzaException:  {self.message}'

    def __repr__(self):
        return f'BitazzaException:  {self.message}'


class Bitazza:
    message_counter = 0

    def __init__(self, api_key, user_id, nounce, signature):
        self.api_key = api_key
        self.user_id = user_id
        self.nounce = nounce
        self.signature = signature
        self.ws = None
        self.ws_url = "wss://apexapi.bitazza.com/WSGateway/"
        self._connect()

    def _send_message(self, function_name: str, payload: dict, message_type: MessageType):
        self._last_function_name = function_name
        self.ws.send(json.dumps(
            {
                "m": message_type,
                "i": self.message_counter,
                "n": function_name,
                "o": json.dumps(
                    payload
                )
            }
        ))


    def _receive_message(self):
        response = self.ws.recv()
        res_json = json.loads(response)
        if res_json['i'] != self.message_counter:
            raise BitazzaException(f'Message id mismatch: {res_json["i"]} != {self.message_counter}')
        self.message_counter += 2
        if 'errorcode' in res_json:
            raise BitazzaException(f'{res_json["errormsg"]} ({res_json["errormsg"]}): {res_json["detail"]}')
        if res_json["m"] == MessageType.REPLY:
            if self._last_function_name == res_json["n"]:
                return json.loads(res_json["o"])
            else:
                raise BitazzaException(f'Function name mismatch: {self._last_function_name} != {res_json["n"]}')
        elif res_json["m"] == MessageType.ERROR:
            raise BitazzaException(f"function={res_json['n']} payload={res_json['o']}")
        elif res_json["m"] == MessageType.EVENT:
            raise NotImplementedError("Event not implemented")
        else:
            raise NotImplementedError("Message type not implemented")

    def _connect(self):
        self.ws = create_connection(self.ws_url)
        self._send_message("AuthenticateUser", {
            "APIKey": self.api_key,
            "Signature": self.signature,
            "UserId": self.user_id,
            "Nonce": self.nounce
        }, MessageType.REQUEST)
        res = self._receive_message()
        if res['errormsg']:
            raise BitazzaException(f'Authentication error: {res["errormsg"]}')
        self.account_id = res['User']['AccountId']
        self.oms_id = res['User']['OMSId']
        self.username = res['User']['UserName']
        return res

    def get_account_info(self, account_id: int=None, oms_id: int=None):
        if account_id is None:
            account_id = self.account_id
        if oms_id is None:
            oms_id = self.oms_id
        self._send_message("GetAccountInfo",
            {
                "accountId": account_id,
                "omsId": oms_id
            },
            MessageType.REQUEST
        )
        return self._receive_message()

    def get_account_balance(self, account_id: int=None, oms_id: int=None):
        if account_id is None:
            account_id = self.account_id
        if oms_id is None:
            oms_id = self.oms_id
        self._send_message("GetAccountPositions",
            {
                "accountId": account_id,
                "omsId": oms_id
            },
            MessageType.REQUEST
        )
        return self._receive_message()
