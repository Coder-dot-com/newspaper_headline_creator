from newspaper_headline_creator.celery import app
from celery import shared_task
from celery.utils.log import get_task_logger
from openai import OpenAI
from decouple import config
import time
from .models import HeadlineRequest

logger = get_task_logger(__name__)



@app.task
def create_headlines_celery(session_id ,uuid):
    try:
        headline_request_object = HeadlineRequest.objects.get(session_id=session_id, unique_id=uuid)
    except HeadlineRequest.DoesNotExist:
        time.sleep(5)
        headline_request_object = HeadlineRequest.objects.get(session_id=session_id, unique_id=uuid)

    #add checks up here
        

    client = OpenAI(
                api_key=config("OPENAI_API_KEY"),
                )
    #call the moderation api and see what it returns



    response = client.moderations.create(input=f"{headline_request_object.input_phrase}")
    output = response.results[0]
    print(output.flagged)

    if output.flagged:
        headline_request_object.response = "Inappropriate input"
        headline_request_object.save()
        return "" 
       
    
    else:

        response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                    "role": "system",
                    "content": "Write in plaintext. Write like a human. Do not use markdown formatting. Do not use * or #. Do not talk about other websites. Do not use numbers. Do not include an introduction. Write a bullet point list. You are a newspaper headline writer."
                    },
                    {
                    "role": "user",
                    "content": f"Generate a list of 10 {headline_request_object.tone} newspaper headlines for the following news article: '{headline_request_object.input_phrase}'"
                    },
                ],
                temperature=1.2,
                max_tokens=4000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
                )

        content = (response.choices[0].message.content).replace("\n", "<br>").replace("*", "").replace("#", "").replace("- ", "")
        

        print('content', content)

        headline_request_object.response = content
        headline_request_object.save()

        #decrement the userai
