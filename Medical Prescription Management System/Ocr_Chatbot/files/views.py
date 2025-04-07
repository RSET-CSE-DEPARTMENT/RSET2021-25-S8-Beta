# from django.http import HttpResponse
# from django.shortcuts import render
# from .models import *
# from django.shortcuts import redirect
# from  django.core.files.storage import FileSystemStorage
# from django.conf import settings
# # import random
# # import pycurl
# # from urllib.parse import urlencode
# # from django.http import FileResponse


# ######AES ENCRYPTION

# # from Crypto.Cipher import AES
# # from Crypto.Random import get_random_bytes
# # from Crypto.Util.Padding import pad, unpad
# # import base64
# # import os


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# import chatbot


# def chat(request):
#     return render(request, 'chat.html')

# @csrf_exempt
# def get_bot_response(request):
#     if request.method == 'GET':
#         message = request.GET.get('message', '')  # Get the 'message' parameter from the query string
#         bot_response=chatbot.talk(message,'chatbot_model')[0]
#         print("user_response:",message)
#         print("bot_response:",bot_response)
#         # TODO: Process the 'message' and generate the bot's response
#         #bot_response = "Hello, I am a bot. You sent: " + message  # Replace this with your actual bot response logic
        
#         response_data = {
#             'response': bot_response,
#         }
        
#         return JsonResponse(response_data)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=400)



from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import chatbot  # Import chatbot module

def chat(request):
    return render(request, 'chat.html')

@csrf_exempt
def get_bot_response(request):
    if request.method == 'GET':
        message = request.GET.get('message', '')  # Get message from request
        bot_response = chatbot.get_response(message)  # Call chatbot function
        
        print("User Input:", message)
        print("Bot Response:", bot_response)
        
        response_data = {
            'response': bot_response,
        }
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
