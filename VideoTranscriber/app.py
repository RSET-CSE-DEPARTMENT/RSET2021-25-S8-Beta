#Flask packages
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

#Process video
from moviepy.editor import VideoFileClip
import os
import sys
import subprocess

#Audio to text transcription
import speech_recognition as sr
from pydub import AudioSegment

#Summarization packages
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.probability import FreqDist
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk import ne_chunk
from nltk.corpus import wordnet
from nltk.corpus import treebank
import math
import random

from googletrans import Translator,LANGUAGES
from indic_transliteration import sanscript
#import pyttsx3

import os
import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision

from transformers import BartForConditionalGeneration, BartTokenizer
import textwrap
from keybert import KeyBERT

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow multiportism
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'    #Hide environment warning messages
os.environ['TF_ENABLE_ONEDNN_OPTS']='0'

# Receive user data from React
userData = []
data={}
@app.route('/signin', methods=['POST'])
def signin():
    global userData
    global data

    data = request.json
    userData.append(data)
    print('Received from React:', data)
    return jsonify({'message': f"Data received! Data = {str(data)} => Username = {data.get('username')}, Password = {data.get('password')}, current userData = {userData}"})

# Send random user data to React
@app.route('/getUser', methods=['GET'])
def get_user():
    print("Data=",data)
    random_user = {'username': data.get('username'), 'password': data.get('password')}
    # return jsonify(random_user)
    return jsonify(userData)

#Clear user database
@app.route('/clearUser', methods=['POST'])
def clear():
    global userData
    data = request.json
    username_to_remove = data.get("username")
    userData = [user for user in userData if user["username"] != username_to_remove]    # Remove user from userData if username matches
    return jsonify({"message": f"User {username_to_remove} removed!", "users": userData})

#Audio to text
def audio2text(audio_path):
    try:
        # Ensure audio file exists
        if not os.path.exists(audio_path):
            return "Error: Audio file not found!"
        print("Audio path:",os.path.exists(audio_path))
        print("Lala5")
        # sound = AudioSegment.from_mp3(audio_path)  # Convert MP3 to WAV
        sound = AudioSegment.from_file(audio_path, format="wav")  # Load WAV
        print("Lala4")
        wav_path = "converted_audio.wav"
        sound.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            total_duration = int(source.DURATION)  # Get total audio duration
            print(f"Total Duration: {total_duration} seconds")

            transcribed_text = []
            for i in range(0, total_duration, 10):  # Process in 10-second chunks
                print(f"Processing chunk: {i}-{i+10}s")
                
                try:
                    audio_chunk = recognizer.record(source, duration=10)
                    text = recognizer.recognize_google(audio_chunk)
                    print("Chunk Text:", text)
                    transcribed_text.append(text)
                except sr.UnknownValueError:
                    transcribed_text.append("[Unclear Audio]")
                except sr.RequestError:
                    transcribed_text.append("[Error with Google API]")

            full_text = " ".join(transcribed_text)
            # print("Final Transcription:", full_text)
            return full_text



    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Speech Recognition service error."
    except Exception as e:
        return f"Error in audio processing: {str(e)}"
    
def timestampify(transcribed_text):
    # ========== STEP 1: Initialize KeyBERT ==========
    kw_model = KeyBERT()

    def extract_topic_keybert(text):
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=1)
        return keywords[0][0].title() if keywords else "General Topic"

    # ========== STEP 2: Segment Transcript Using Real Duration ==========
    def segment_transcript_text(transcript_text, total_video_duration, wrap_width=100):
        print("Entered segmentation part")
        lines = textwrap.wrap(transcript_text, width=wrap_width)
        output = ""
        topic_tracker = {}
        topic_counter = 0

        # Dynamically divide video duration across all chunks
        duration_per_chunk = total_video_duration / len(lines) if lines else 0
        current_time = 0.0

        for line in lines:
            next_time = round(current_time + duration_per_chunk, 2)
            topic = extract_topic_keybert(line)

            if topic not in topic_tracker:
                topic_tracker[topic] = topic_counter
                output += f"\n=== Topic {topic_counter}: {topic} ===\n"
                topic_counter += 1

            output += f"[{current_time:.2f}s - {next_time:.2f}s] {line}\n"
            current_time = next_time

        return output.strip()

    # ========== STEP 3: Get Video Duration ==========
    def get_video_duration(video_path="temp_video.mp4"):
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()
        print("Duration kitti-",duration)
        return duration

    # ========== STEP 4: Use Transcript + Real Video ==========
    def process_transcript_with_video(transcript_text, video_path="temp_video.mp4"):
        print("Fetching video duration...")
        duration = get_video_duration(video_path)
        
        print("Segmenting transcript using KeyBERT with real timestamps...")
        return segment_transcript_text(transcript_text, duration)

    # ========== Example Run ==========
    transcript_text = """
    supervised and unsupervised learning super is one which train the model with label there which are the model this is what the right opposite should be based on this learning is we just provide the data so why you want type of learning of the other what say you want to know the project which products are customers likely to buy based on the process history when supervised learning would be the better approach for example if you tell my also be able to protect 
    """

    output = process_transcript_with_video(transcribed_text, "temp_video.mp4")
    print(output)
    return(output)

@app.route('/videotranscribe',methods=['POST','GET'])
def videotranscribe():
    video = request.files.get('video')
    url_id = request.form.get('video_url_id')
    if(url_id): video_url = "https://www.youtube.com/watch?v="+url_id
    # print(video,"or",video_url)

    audio_path = "downloaded_audio.wav"

    try:
        if video and not url_id:
            # Save video file temporarily
            temp_video_path = "temp_video.mp4"
            video.save(temp_video_path)

            # Extract video audio
            video_clip = VideoFileClip(temp_video_path)
            # video_clip.audio.write_audiofile(audio_path) #for mp3
            video_clip.audio.write_audiofile(audio_path, codec='pcm_s16le')  # Use PCM format

            # **Close the video file properly**
            video_clip.close()

            # open(audio_path, 'w').close()

            # Clean up temp video file
            os.remove(temp_video_path)

        elif url_id:
            # Download audio directly in mp3 format
            # Using subprocess to display progress
            command = f'yt-dlp -x --audio-format wav -o "{audio_path}" "{video_url}" --keep-video'
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            # Real-time progress monitoring
            for line in iter(process.stdout.readline, b''):
                sys.stdout.write(line.decode())
                sys.stdout.flush()

            process.wait()
            if os.path.exists(audio_path):
                try:
                    # files.download(audio_path)
                    print("Audio file is ready for download.")
                except Exception as e:
                    print("There was an error downloading the audio file:", e)
            else:
                print("Audio file not found. Please check the URL and try again.")
            # print("Audio downloaded and saved as MP3.")


        transcribed_text=audio2text(audio_path)
        print("Transcribed text:\n\n",transcribed_text)
        # timestampedText=timestampify(transcribed_text) or ''
        # print("\n\nTimestamped text: \n\n",timestampedText)
        return jsonify({'message': 'Transcription started!','audio_path':audio_path,'transcript':transcribed_text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'No video file provided'}), 400

#Extractive Summarization
text1, tst, sentences='','',''
stop_words={}
def extsum():
  global text1, tst, sentences  # ✅ Declare global variables

  #Summarize
  #Processing
  wordFreq=FreqDist(text1)
  #print("\nWord Frequency:\n")
  #for i in wordFreq :print(i,":",wordFreq[i])

  text=tst
  sentFreq={}
  for sent in sentences:
    for word in word_tokenize(sent.lower()):
      if word in wordFreq:                                      #It is a relevant word
        if sent not in sentFreq:
          sentFreq[sent]=wordFreq[word]                         #Initialize count
        else:
          sentFreq[sent]+=wordFreq[word]                        #Add frequency to total count

  n=int(math.ceil(0.8*len(sentences)))                                          #Select top 80% sentences
  summary=sorted(sentFreq, key=sentFreq.get, reverse=True)      #Sort sentences in descending order based on freq score and displays list of sentences from most frequent to the least frequent.
  print(summary)
  summary=" ".join(summary[:n])                                 #'n' lines summary
  print(summary,sentences,n)

  st=""
  for i in sent_tokenize(summary):
    for j in word_tokenize(i):
      if '.' in j and len(j)>1:st+=j.replace('.','. \n')
      else:st+=j+" "
    st+="\n"
  return st

#Abstractive summarization
def abssum():
    model_name = "facebook/bart-large-cnn"
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    text = tst
    sum=""
    c=1
    for i in text.split("\n\n"):
        if i.strip():
            # Prepare the input text for the model
            print(f"Summarizing paragraph {c}...",end=" ")
            inputs = tokenizer.encode("summarize: " + i, return_tensors="pt", max_length=10000, truncation=True)

            # Generate summary
            summary_ids = model.generate(
                inputs,
                max_length=256,         # Adjusted maximum length for output  (500)
                min_length=64,          # Adjusted minimum length for output (100)
                length_penalty=2,     # Reduced length penalty for longer summaries (5)
                num_beams=8,            # Reduced number of beams for diversity  (17)
                do_sample=True,         # Enable sampling for more diverse output
                top_k=50,               # Limit to top-k candidates
                top_p=0.95,             # Use nucleus sampling for diversity
                early_stopping=True      # Stop when the best result is found
            )

            # Decode the summary
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            sum+=summary+"\n\n"
            print(f"Done...")
            c+=1

    st=""
    for i in sum.split("\n"):
        if i.strip():st+=i.replace(".",". \n")
        else:st+="\n\n"

    print(st)
    return st

@app.route('/summarization',methods=['POST'])
def summarize():
    global text1, tst, sentences, stop_words  # ✅ Declare global variables

    option=int(request.json['option'])

    #Select dummy text
    text=request.json['transcript']

    # Initialize translator
    translator = Translator()

    # Initialize translated text storage
    tst = ""
    for i in text.split("\n\n"):
        if i.strip():                                                             # Skip any empty or whitespace-only paragraphs
            detection = translator.detect(i)
            if detection and detection.lang:                                      # Check if detection was successful
                lang = LANGUAGES.get(detection.lang, "unknown")                   # Default to 'unknown' if lang is not in LANGUAGES
                trans = translator.translate(i, src=detection.lang, dest="en")
                tst += trans.text + "\n\n"
            else:
                print("Language detection failed for a paragraph.")
                # %tensorflow_versionst += i + "\n\n"  # Keep original if detection fails

    # Final translated text
    print("Detected language:", detection.lang, f"({lang})")
    print("\nTranslated text:\n", tst)


    stop_words=set(stopwords.words('english'))

    #Pre-processing text
    #Tokenizing to sentences and removing stopwords
    text1=[]
    sentences=sent_tokenize(tst)
    for i in sentences:
        w=word_tokenize(i)  #Can't use split() because we want to separate ., ,, (, ), etc.
        #print(w,"\n")
        for j in w:
            if j not in stop_words:       #Store keywords
                text1+=[j]

    words = word_tokenize(tst) # Tokenize the text
    print(words)
    tagged_words = pos_tag(words) # Get part-of-speech tags
    text1=[word for word, tag in tagged_words if tag in ('NN', 'NNS', 'NNP', 'NNPS')] # Extract nouns and proper nouns

    #After removing stopwords
    print("\nText after removing stopwords:\n")
    for i in text1:
        if '.' in i and len(i)>1:           #Eg: "text.document" -> ['text','.','document']
            text1.remove(i)
            text1+=list(i.partition('.'))     #We can simply use i.replace('.','. ')
    print(text1)
    summary = extsum() if option==1 else abssum()

    #Keywords extraction
    summary=summary.replace("[ Unclear Audio ]"," ")
    print("\n\n\nsummary=",summary+"\n\n\n")
    words = word_tokenize(summary) # Tokenize the text
    tagged_words = pos_tag(words) # Get part-of-speech tags
    kw=[word for word, tag in tagged_words if tag in ('NN', 'NNS', 'NNP', 'NNPS') and word!="’"] # Extract nouns and proper nouns

    # Sort based on frequency in the original list, in descending order
    kw = sorted(kw, key=lambda x: kw.count(x), reverse=True)

    # Remove duplicate words
    temp=[]
    for i in kw:
        if i.lower() not in temp:
            temp+=[i]

    c=0
    srclist=[]
    for word in temp:
        if c%10==0 and c!=0:print("\n")
        srclist.append([word,kw.count(word)])
        print([word,f"({kw.count(word)})"],end=", ")      #Keyword and count
        c+=1

    #Translated summary
    trans_text=""
    if detection.lang!='en':
        trans_text=translator.translate(summary,src="en",dest=detection.lang).text
        print("\n",trans_text)
    return jsonify({"summary":summary,"translation":trans_text,"searchlist":srclist})

@app.route('/SearchAndFilter',methods=['POST','GET'])
def SaF():
    summary = request.json["summary"]
    src = request.json["search"]
    print("Got summary from frontend:\n",summary)
    print("Got search from frontend: ",src)
    words = word_tokenize(summary) # Tokenize the text
    tagged_words = pos_tag(words) # Get part-of-speech tags
    kw=[word for word, tag in tagged_words if tag in ('NN', 'NNS', 'NNP', 'NNPS') and word!="’"] # Extract nouns and proper nouns

    # Sort based on frequency in the original list, in descending order
    kw = sorted(kw, key=lambda x: kw.count(x), reverse=True)

    # Remove duplicate words
    temp=[]
    for i in kw:
        if i.lower() not in temp:
            temp+=[i]

    ps=PorterStemmer()
    # lemmatizer=WordNetLemmatizer()
    c=0
    sentFound=[]
    print("For you: ")
    for i in temp:
        if c%10==0 and c!=0:print("\n")
        print([i,f"({kw.count(i)})"],end=", ")
        c+=1
    # src=input("\nEnter keyword:")
    if src.lower()!="x":
        # srclist=grammatize(src)
        for i in sent_tokenize(summary):
            if src in i.lower() or ps.stem(src) in i.lower():
                sentFound.append([i])
                print([i])
    else:print("Thank you")
        
    return jsonify({"message":"Ivide ethi","sentence":sentFound})

#Text to Sign Images
video_urls=[]
sign_images={
 'a':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-249702187.jpg',
 'b':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-249702181.jpg',
 'c':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-50057038.jpg',
 'd':'https://www.shutterstock.com/shutterstock/photos/328842020/display_1500/stock-photo-finger-spelling-the-alphabet-in-american-sign-language-asl-the-letter-d-328842020.jpg',
 'e':'https://www.shutterstock.com/image-photo/alphabet-letter-e-spelling-by-260nw-2121947243.jpg',
 'f':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-249702058.jpg',
 'g':'https://www.shutterstock.com/image-photo/deaf-sign-alphabet-g-american-260nw-2529959423.jpg',
 'h':'https://static1.bigstockphoto.com/7/0/1/large2/107236079.jpg',
 'i':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-249702073.jpg',
 'j':'https://www.shutterstock.com/image-vector/hand-sign-language-letter-j-600nw-2367694385.jpg',
 'k':'https://www.shutterstock.com/shutterstock/photos/50057062/display_1500/stock-photo-finger-spelling-the-alphabet-in-american-sign-language-asl-the-letter-k-50057062.jpg',
 'l':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-425224252.jpg',
 'm':'https://www.shutterstock.com/shutterstock/photos/328841975/display_1500/stock-photo-finger-spelling-the-alphabet-in-american-sign-language-asl-the-letter-m-328841975.jpg',
 'n':'https://www.shutterstock.com/shutterstock/photos/249702079/display_1500/stock-photo-finger-spelling-the-alphabet-in-american-sign-language-asl-the-letter-n-249702079.jpg',
 'o':'https://www.shutterstock.com/shutterstock/photos/249702076/display_1500/stock-photo-finger-spelling-the-alphabet-in-american-sign-language-asl-the-letter-o-249702076.jpg',
 'p':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-50057077.jpg',
 'q':'https://thumbs.dreamstime.com/b/alphabet-letter-q-sign-language-deaf-fingerspelling-american-sign-language-asl-hand-gesture-letter-q-white-187333908.jpg',
 'r':'https://static1.bigstockphoto.com/6/3/7/large2/7368476.jpg',
 's':'https://c8.alamy.com/comp/DBB70M/finger-spelling-the-alphabet-in-american-sign-language-asl-the-letter-DBB70M.jpg',
 't':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-50057089.jpg',
 'u':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-249702025.jpg',
 'v':'https://c8.alamy.com/comp/JADW3G/finger-spelling-the-alphabet-in-american-sign-language-asl-the-letter-JADW3G.jpg',
 'w':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-260nw-328842080.jpg',
 'x':'https://www.shutterstock.com/image-photo/finger-spelling-alphabet-american-sign-600w-249702049.jpg',
 'y':'https://www.shutterstock.com/image-photo/letter-y-finger-spelling-alphabet-260nw-497573854.jpg',
 'z':'https://www.shutterstock.com/shutterstock/photos/41803117/display_1500/stock-photo-how-to-sign-the-letter-z-using-american-sign-language-41803117.jpg'
}

@app.route('/get_signs', methods=['POST', 'GET'])
def get_signs():
    global stop_words, video_urls, sign_images
    stop_words=set(stopwords.words('english'))
    # print(stop_words)
    summary=request.json["summary"]

    def get_url(word):
        x=word.lower()
        if word.lower() not in stop_words:
            if word.lower()=='i':word='me'
            elif word.lower()=='education':word='learn'
            elif word.lower()=="learning":word="learn"
        url=f"https://www.handspeak.com/word/{x[0]}/{x[:3]}/{x}.mp4"
        return url
    
    # sample = "renewable"
    # sample = "i love learn mathematics"
    sample = summary
    words=sample.split()
    sign_images_js = json.dumps(sign_images)
    videoUrls=[get_url(i) for i in words]  #Get url for each word
    return jsonify({"message":"Sending you video url array","videoUrls":videoUrls,"words":words, "signImages":sign_images})

# Show questions
@app.route('/showQuestions', methods=['POST', 'GET'])
def showQuestions():
    summary=request.json["summary"]
    dumsum=summary.replace('\n','')
    dumsum=dumsum.lower()
    kw=request.json["keywords"]
    num_questions = int(request.json["numQuestions"])
    choice=request.json["optionValue"]

    # Initialize performance tracking
    performance = {
        "fill_blank": {"correct": 0, "incorrect": 0},
        "mcq": {"correct": 0, "incorrect": 0},
        "multi_blank": {"correct": 0, "incorrect": 0}
    }

    question_array=[]
    answer_array=[]

    # Function for generating fill-in-the-blank questions
    def mfitb(num_questions):
        print("\nFill in the Blanks:\n")

        for i in range(num_questions):
            ans = random.choice(kw)
            answer_array.append(ans)
            if ans in dumsum:
                sent = [sentence for sentence in sent_tokenize(dumsum) if ans in sentence]
                if sent:
                    qn_sentence = random.choice(sent).replace(ans, "__________")
                    question_array.append(qn_sentence)
                    # print(f"Question: {qn_sentence}")
                    # res = input("Enter your answer: ").strip().lower()
                    # if res == ans:
                    #     print("Correct!\n")
                    #     performance["fill_blank"]["correct"] += 1
                    # else:
                    #     print(f"Incorrect. The correct answer is: {ans.capitalize()}\n")
                    #     performance["fill_blank"]["incorrect"] += 1
        print("Questions=",question_array)
        return jsonify({"questions":question_array, "answers":answer_array})

    # Function for Multiple Choice Questions (MCQs)
    def dmcq(num_questions):
        print("\nMultiple Choice Questions:\n")
        for i in range(num_questions):
            ans = random.choice(kw)
            if ans in dumsum:
                sent = [sentence for sentence in sent_tokenize(dumsum) if ans in sentence]
                if sent:
                    qn_sentence = random.choice(sent).replace(ans, "__________")
                    options = [ans]
                    while len(options) < 4:
                        option = random.choice(kw)
                        if option != ans and option not in options:
                            options.append(option)
                    random.shuffle(options)

                    print(f"Question: {qn_sentence}")
                    for j, option in enumerate(options):
                        print(f"{j + 1}. {option.capitalize()}")

                    try:
                        user_choice = int(input("Enter the option number: "))
                        if options[user_choice - 1] == ans:
                            print("Correct!\n")
                            performance["mcq"]["correct"] += 1
                        else:
                            print(f"Incorrect. The correct answer is: {ans.capitalize()}\n")
                            performance["mcq"]["incorrect"] += 1
                    except (ValueError, IndexError):
                        print("Invalid input. Please select a valid option.\n")
                        performance["mcq"]["incorrect"] += 1

    # Function for generating multiple blanks questions
    def multi_blank(num_questions):
        print("\nMultiple Blanks Questions:\n")
        for i in range(num_questions):
            answers = random.sample(kw, 2)  # Select two random keywords
            if all(ans in dumsum for ans in answers):
                sent = [sentence for sentence in sent_tokenize(dumsum) if all(ans in sentence for ans in answers)]
                if sent:
                    qn_sentence = random.choice(sent)
                    for ans in answers:
                        qn_sentence = qn_sentence.replace(ans, "__________", 1)
                        print(qn_sentence,ans)
                    print(f"Question: {qn_sentence}")
                    res1 = input("Enter first answer: ").strip().lower()
                    res2 = input("Enter second answer: ").strip().lower()

                    if res1 == answers[0] and res2 == answers[1]:
                        print("Correct!\n")
                        performance["multi_blank"]["correct"] += 1
                    else:
                        print(f"Incorrect. The correct answers are: {answers[0].capitalize()}, {answers[1].capitalize()}\n")
                        performance["multi_blank"]["incorrect"] += 1
    if choice == "1": mfitb(num_questions)
    elif choice == "2": dmcq(num_questions)
    elif choice == "3": multi_blank(num_questions)
    return jsonify({"message":"Summary for question kittitundu","questions":question_array,"answers":answer_array})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

#Video Samples
#https://www.youtube.com/watch?v=SqcY0GlETPk (sample video-large)
#https://www.youtube.com/watch?v=YcOdGAnJlOc (sample video-small)
#https://youtu.be/XUGyuG4L2uM?si=BqBLg4GkbkPMnL5H (30 second video)
