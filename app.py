from flask import Flask, render_template, request,session,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
import os
import requests
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
import pandas
from flask import request as req
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer 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"}
# import count_vect
from googletrans import Translator, constants
from pprint import pprint
# init the Google API translator
translator = Translator()
from flask import Flask, jsonify, request
from pytube import YouTube
from flask import request as req
import requests
#from huggingsound import SpeechRecognitionModel
from transformers import SpeechEncoderDecoderModel
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
from googletrans import Translator

import ffmpeg
import soundfile as sf
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
import torch
#import librosa
from moviepy.editor import AudioFileClip
import numpy as np
device = "cuda" if torch.cuda.is_available() else "cpu"


import re

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__,template_folder='templates')
app.secret_key = 'super-secret-key'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_password']
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    uname = db.Column(db.String(50), nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(10), nullable=False)
    cpassword = db.Column(db.String(10), nullable=False)

class Contact(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False)
    subject=db.Column(db.String(50),nullable=False)
    message=db.Column(db.String(250),nullable=False)

@app.route("/")
def Home():
    return render_template('index.html',params=params)

@app.route("/about.html")
def About():
    return render_template('about.html',params=params)



@app.route("/register.html", methods=['GET','POST'])
def register():
    if(request.method=='POST'):
        name = request.form.get('name')
        uname = request.form.get('uname')
        mobile = request.form.get('mobile')
        email= request.form.get('email')
        password= request.form.get('password')
        cpassword= request.form.get('cpassword')

        user=Register.query.filter_by(email=email).first()
        if user:
            flash('Account already exist!Please login','success')
            return redirect(url_for('register'))
        if not(len(name)) >3:
            flash('length of name is invalid','error')
            return redirect(url_for('register')) 
        if (len(mobile))<10:
            flash('invalid mobile number','error')
            return redirect(url_for('register')) 
        if (len(password))<8:
            flash('length of password should be greater than 7','error')
            return redirect(url_for('register'))
        else:
             flash('You have registtered succesfully','success')
            
        entry = Register(name=name,uname=uname,mobile=mobile,email=email,password=password,cpassword=cpassword)
        db.session.add(entry)
        db.session.commit()
    return render_template('register.html',params=params)

@app.route("/login.html",methods=['GET','POST'])
def login():
    if (request.method== "GET"):
        if('email' in session and session['email']):
            return render_template('dash.html',params=params)
        else:
            return render_template("login.html", params=params)

    if (request.method== "POST"):
        email = request.form["email"]
        password = request.form["password"]
        
        login = Register.query.filter_by(email=email, password=password).first()
        if login is not None:
            session['email']=email
            return render_template('dash.html',params=params)
        else:
            flash("plz enter right password",'error')
            return render_template('login.html',params=params)

@app.route("/contact.html",  methods=['GET','POST'])
def contact():
    if(request.method =='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        subject=request.form.get('subject')
        message=request.form.get('message')
        entry=Contact(name=name,email=email,subject=subject,message=message)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',params=params)


@app.route("/logout", methods = ['GET','POST'])
def logout():
    session.pop('email')
    return redirect(url_for('Home')) 


@app.route("/dash.html")
def dashboard():
    return render_template("dash.html")

@app.route('/dash',methods=["GET","POST"])
def Fill_data():
    if req.method=="POST":
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer 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"}
        youtube_video =req.form["url"]
        video_id = youtube_video.split("=")[1]
        yt = YouTube(youtube_video)
        yt.streams \
        .filter(only_audio = True, file_extension = 'mp4') \
        .first() \
        .download(filename = 'ytaudio.mp4')
        video_file_name = "ytaudio.mp4"
        transcribed_audio_file_name = "ytaudio.wav"
        audioclip = AudioFileClip(video_file_name)
        audioclip.write_audiofile(transcribed_audio_file_name)
        import speech_recognition as sr
        r = sr.Recognizer()
        def get_large_audio_transcription(path):
            sound = AudioSegment.from_wav(path)
            chunks = split_on_silence(sound,
            min_silence_len = 500,
            silence_thresh = sound.dBFS-14,
            keep_silence=500,)
            folder_name = "audio-chunks"
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            whole_text = ""
            for i, audio_chunk in enumerate(chunks, start=1):
                chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                with sr.AudioFile(chunk_filename) as source:
                    audio_listened = r.record(source)
                    try:
                        text = r.recognize_google(audio_listened)
                    except sr.UnknownValueError as e:
                        print("Error:", str(e))
                    else:
                        text = f"{text.capitalize()}. "
                        print(chunk_filename, ":", text)
                        whole_text += text
            return whole_text
        path = "ytaudio.wav"
        collect = (get_large_audio_transcription(path))
        data = collect
        minL=30
        maxL = 80
        def query(payload):
            response = requests.post(API_URL,headers=headers,json=payload)
            return response.json()
        output = query(
            {
                "inputs" : data,
                "parameters":{"min_length":minL,"max_length": maxL},
            }
        )[0]
        return render_template("dash.html",data=data,result=output["summary_text"])
    return render_template("dash.html")

@app.route("/translate_lang",methods=["POST"])
def translate_lang():
    if request.method =="POST":
        sentence = str(request.form.get("sentence"))
        code = str(request.form.get("code"))
        print(sentence)
        translator = Translator()
        translated_sentence = translator.translate(sentence,src="en",dest=code)
        translated = translated_sentence.text
    return render_template("index2.html",language_selected = code,sentence=sentence,translated_res = translated)

@app.route("/translate_lang")
def index():
    lang = [{"name":"English","code":"en"},{"name":"Marathi","code":"mr"},{"name":"Hindi","code":"hi"}]
    return render_template("index2.html",languages = lang)

if __name__ == '__main__':
    app.run(debug=True)