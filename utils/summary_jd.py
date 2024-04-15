from langchain_core.output_parsers import JsonOutputParser
from scripts.chat_templates import chat_template_summary_jd
from configs.llm_model import llm

# define the parser object
parser = JsonOutputParser()

def summary_jd(jobdes: str):
    # create the chat message
    chat_message =  chat_template_summary_jd.format_messages(jd=jobdes)
    result = llm.invoke(chat_message)
    
    return result.content