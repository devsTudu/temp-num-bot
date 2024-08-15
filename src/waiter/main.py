from telegram.bot import bot,logger
from .query_handler import answer_to
from .message_handler import respond_to


async def workOn(request):
    if 'callback_query' in request:
        return await answer_to(request)
    elif 'message' in request:
        return await respond_to(request)
    else:
        print(request)
        logger.warning("Unusual Request")


#Set the Webhook
def setWebhook(url):
    data = {
        "url":url
    }
    return data
    return bot.send_request("setWebhook",data)

