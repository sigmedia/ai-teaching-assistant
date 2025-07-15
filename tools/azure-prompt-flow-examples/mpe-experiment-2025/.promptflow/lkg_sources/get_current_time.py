from promptflow import tool
from datetime import datetime
import pytz

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def get_ireland_time(chat_input: str) -> str:
    ireland_timezone = pytz.timezone('Europe/Dublin')
    current_time = datetime.now(ireland_timezone)
    formatted_time = current_time.strftime("%A, %B %d, %Y, %H:%M:%S")
    return formatted_time