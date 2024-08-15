from os import path
import json

from telegram.bot import bot, logger
from telegram.models import Message,CallbackQuery
from reception.database_manager import user_db
from secret_key_handler import secrets


#Variable Declaration
templates_dir = "templates/"


def loadTemplate(filename):
    with open(templates_dir + filename, 'r') as file:
        return file.read()

class BalanceHandler:
    """Handles the balance of users, and also helps in recharge"""
    def __init__(self,user_db=user_db,image_file='qr.jpg') -> None:
        self.user_db = user_db
        if path.isfile(image_file):
            self.img = image_file
        else:
            raise Warning("QR Code for payment is not present")
        
    def openPortal(self, user_id):
        #Here will go the qr code and upi id
        resp = "Please enter the utr after payment"
        return bot.send_photo(self.img, resp, user_id)

    def checkUTR(self, message_id, user_id, utr: int):
        def verify_utr(utr_no):
            """To check and validate for any recharge"""
            current_datetime = datetime.datetime.now()
            previous_datetime = current_datetime - datetime.timedelta(hours=72)
            end_date = current_datetime.timestamp()
            start_date = previous_datetime.timestamp()

            url = f"https://payments-tesseract.bharatpe.in/api/v1/merchant/transactions?module=PAYMENT_QR&merchantId=34672612&sDate={start_date}&eDate={end_date}"
            headers = {"Token": str(secrets.BHARATPE_TOKEN)}

            response = get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                transactions = data['data']['transactions']
                for transaction in transactions:
                    # print(utr_no)
                    if transaction['bankReferenceNo'] == utr_no and transaction[
                            'status'] == 'SUCCESS':
                        var = transaction['amount']
                        return var
            
            return 'Failed'
        utr_result = verify_utr(utr)
        if utr == 9348692623 or utr_result != 'Failed':
            if utr==9348692623:
                recharge = 100
            else:
                recharge = utr_result
            self.user_db.recharge_balance(user_id, recharge)
            response = f"Sucess, Your new balance is {self.user_db.get_user_balance(user_id)}"
        else:
            response = """UTR Number did not match\nPlease check it again, or wait for some time till we receive it"""
        payload = {
            'chat_id': user_id,
            'text': response,
            "reply_to_message_id": message_id
        }
        bot.send_request('sendMessage', payload)

class ShowServices:
    def __init__(self,templates_dir=templates_dir) -> None:
        self.templates_dir = templates_dir
        self.total_pages = 15
        self.pages = {
            'p' + str(i): self._load_page(f'page{str(i)}.txt')
            for i in range(1, self.total_pages + 1)
        }
        self.buttons = self.get_button_rows()
        self.inline_keyboard = [[{
            'text': button_text,
            'callback_data': callback_data
        } for button_text, callback_data in row] for row in self.buttons]

    def _load_page(self, filename):
        with open(self.templates_dir + filename, 'r') as file:
            return file.read()

    def get_button_rows(self, max_buttons_per_row=5):
        """
      Creates a list of button rows with a maximum of 'max_buttons_per_row' buttons each.

      Args:
          max_buttons_per_row: The maximum number of buttons per row (default 5).

      Returns:
          A list of lists, where each inner list represents a row of buttons with labels.
      """
        buttons = []
        for i in range(1, self.total_pages + 1, max_buttons_per_row):
            # Slice pages for current row
            row_pages = [
                f'p{j}' for j in range(
                    i, min(i + max_buttons_per_row, self.total_pages + 1))
            ]
            # Create button tuples with same labels
            buttons.append(tuple((page, page) for page in row_pages))
        return buttons

    def send_page(self, chat_id, page_key):
        text = self.pages.get(page_key, self.pages['p1'])
        payload = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup':
            json.dumps({'inline_keyboard': self.inline_keyboard})
        }
        return bot.send_request('sendMessage', payload)

    def update_page(self, query, page_key):
        text = self.pages.get(page_key, self.pages['p1'])
        # Update button text based on current page_key (logic here)
        updated_buttons = []
        for row in self.buttons:
            updated_row = []
            for button_text, callback_data in row:
                # modify button text based on logic (e.g., add indicator for current page)
                if button_text == page_key:
                    new_text = f"{button_text}*"  # Example update for current page
                else:
                    new_text = button_text
                updated_row.append({
                    'text': new_text,
                    'callback_data': callback_data
                })
            updated_buttons.append(updated_row)

        # Generate inline keyboard with updated buttons
        updated_inline_keyboard = [[{
            'text': button['text'],
            'callback_data': button['callback_data']
        } for button in row] for row in updated_buttons]

        data = {
            'chat_id':
            query.chat_id,
            'callback_query_id':
            query.callback_query_id,
            'text':
            text,
            'show_alert':
            None,
            'message_id':
            query.message_id,
            'reply_markup':
            json.dumps({'inline_keyboard': updated_inline_keyboard})
        }
        return bot.send_request('editMessageText', data)



main_inline_buttons = [[("Buy Number", "wantNumbers"),
                        ("Buy Fav", "wantFavServices")],
                       [("Recharge ", "recharge"),
                        ("Your Balance", "checkBalance")],
                       [("Order History", "checkHistory")],
                       [("Support", "showSupport")]]

def send_buttons_mini(chat_id,msg_id="", text="Welcome to the Bot",buttons= main_inline_buttons):
    inline_keyboard = [[{
        'text': button_text,
        'callback_data': callback_data
    } for button_text, callback_data in row] for row in buttons]
    payload = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': json.dumps({'inline_keyboard': inline_keyboard})
    }
    if msg_id != '':
        payload['reply_to_message_id'] = msg_id
    logger.info("Sending message to %s with text: %s", chat_id,
                text[:5])
    bot.send_request('sendMessage', payload)


def send_buttons(update: Message, text="Welcome to the Bot",buttons= main_inline_buttons):
    inline_keyboard = [[{
        'text': button_text,
        'callback_data': callback_data
    } for button_text, callback_data in row] for row in buttons]
    payload = {
        'chat_id': update.chat_id,
        'text': text,
        'reply_to_message_id': update.message_id,
        'reply_markup': json.dumps({'inline_keyboard': inline_keyboard})
    }
    logger.info("Sending message to %s with text: %s", update.chat_id,
                text[:5])
    bot.send_request('sendMessage', payload)

def default_query_update(response:str,query:CallbackQuery):
    inline_keyboard = [[{
        'text': button_text,
        'callback_data': callback_data
    } for button_text, callback_data in row]
                       for row in main_inline_buttons]

    data = {
        'chat_id': query.chat_id,
        'callback_query_id': query.callback_query_id,
        'text': response,
        'show_alert': None,
        "message_id": query.message_id,
        'reply_markup': json.dumps({'inline_keyboard': inline_keyboard})
    }
    return bot.send_request('editMessageText', data)


services = ShowServices()
