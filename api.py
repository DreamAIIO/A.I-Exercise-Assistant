from feedback import create_messages, get_feedback
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

app = FastAPI() 

class User_input(BaseModel):
    video : str

@app.post("/messagesFeedback", response_class=PlainTextResponse)
def operate(u_input:User_input):
    messages = create_messages(u_input.video)
    feedback = get_feedback(messages)
    return feedback



