from newspaper_headline_creator.celery import app
from celery import shared_task
from celery.utils.log import get_task_logger
from openai import OpenAI
from decouple import config
import time
from .models import HeadlineRequest
from datetime import datetime, timedelta
from django.utils import timezone
from tiers.models import UserTier, Tier

logger = get_task_logger(__name__)



@app.task
def create_headlines_celery(headline_request_uuid, session):
    try:
        headlines_request_object = HeadlineRequest.objects.get(unique_id=headline_request_uuid)
    except HeadlineRequest.DoesNotExist:
        time.sleep(5)
        headlines_request_object = HeadlineRequest.objects.get(unique_id=headline_request_uuid)

    #add checks up here
        
    user_ai = headlines_request_object.user_ai

    client = OpenAI(
                api_key=config("OPENAI_API_KEY"),
                )
    #call the moderation api and see what it returns


    if user_ai.monthly_ai_credits_remaining < 1 and user_ai.purchased_ai_credits_remaining < 1:
        headlines_request_object.response = "Error no ai credits left"
        headlines_request_object.save()
        return "" 

    response = client.moderations.create(input=f"{headlines_request_object.input_phrase}")
    output = response.results[0]
    print(output.flagged)

    if output.flagged:
        headlines_request_object.response = "Inappropriate input"
        headlines_request_object.save()
        return "" 
       
    
    else:

        response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                    "role": "system",
                    "content": "Write in plaintext. Write like a human. Do not use markdown formatting. Do not use * or #. Do not talk about other websites. Do not use numbers. Do not include an introduction. Write a bullet point list"
                    },
                    {
                    "role": "user",
                    "content": f"Generate a list of 10 product ideas for: '{headlines_request_object.input_phrase}'"
                    },
                ],
                temperature=1.2,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
                )

        content = (response.choices[0].message.content).replace("\n", "<br>").replace("*", "").replace("#", "").replace("- ", "")
        

        print('content', content)

        headlines_request_object.response = content
        headlines_request_object.save()

        #decrement the userai

        if user_ai.monthly_ai_credits_remaining > 0:

            user_ai.monthly_ai_credits_remaining -=1
        else:
            user_ai.purchased_ai_credits_remaining -=1
        
        user_ai.save()
