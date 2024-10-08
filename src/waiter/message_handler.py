from cook.main import serviceOps
from reception.database_manager import user_db

from telegram.bot import bot, logger
from telegram.models import Message

from .helper import BalanceHandler, loadTemplate, send_buttons, services
from .helper_phone import showAvailableServer


#Command Handler
class Commands:
    def __init__(self,update:Message) -> None:
        self.update = update
        self.name = update.user_username
        self.user_id = update.user_id
        self.commands_map ={
            "/start":self.start,
            "/getnum":self.getnum,
            "/checkbal":self.checkbal,
            "/recharge":self.recharge,
            "/seefav":self.getfavlist,
            "/seehist":self.checkhistory,
            "/referal":self.getreferral
        }
        
    def run(self):
        command = self.update.text
        if "ser_" in command:
            service_code = str(command)[5:]
            # This will check for the available services for this number
            return showAvailableServer(service_code,self.update)
        try:
            return self.commands_map[command]()
        except KeyError as e:
            logger.error(str(e))
            bot.reply_message(self.user_id,self.update.message_id,
                            "Invalid Command")
            
        
    def start(self):
        welcome_msg = loadTemplate("welcome_message.txt")
        response = f"Hi, {self.name}, welcome to the \n"
        response += welcome_msg
        return send_buttons(self.update,response)

    def getnum(self):
        return services.send_page(self.user_id, 1)

    def checkbal(self):
        bal = user_db.get_user_balance(self.user_id)
        response = f"Your Balance is {bal} "
        return send_buttons(self.update,response)

    def recharge(self):
        return BalanceHandler().openPortal(self.user_id)

    def checkhistory(self):
        response = " Check History here\n"
        txn = user_db.get_user_transactions(self.user_id)
        response += "\n".join("{:<4} {:<10}".format(i[-1], i[2]) for i in txn)
        return send_buttons(self.update,response)
    
    def getfavlist(self):
        return send_buttons(self.update,"Your Favourite List appears here")
    
    def getreferral(self):
        return send_buttons(self.update,"Your referral scores")
        

#Handle the messages
async def respond_to(request):
    try:
        update = Message(request)
        logger.info("%s messaged: %s",
                    update.user_first_name, update.text)
    except Exception as e:
        logger.critical("Invalid Message request")
        raise e from None
    if update.is_command:
        commands = Commands(update=update)
        commands.run()
    elif update.text.isdigit():
        BalanceHandler().checkUTR(update.message_id, update.user_id,
                                  int(update.text))
    elif "/" not in update.text:
        sendSearchResult(update)
    else:
        return bot.reply_message(update.chat_id, update.message_id,
                          "We are working on it")


#Handle Search Query
def sendSearchResult(update: Message):
    result = serviceOps.fuzzy_search(update.text, 50)
    if "Not" in result:
        response = "Sorry the search term didn't match with any service we offer"
    else:
        response = "Are you looking for them.."
        for index, element in enumerate(result):
            response += f"\n{index+1} {element[1]} /ser_{element[2]}"
    bot.send_message(update.chat_id, response)     

