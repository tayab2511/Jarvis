import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
import json
import time
from gtts import gTTS
import pygame
import os
from dotenv import load_dotenv


recognizer = sr.Recognizer()
engine = pyttsx3.init()
load_dotenv()
newsapi = os.getenv("NEWS_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_site_url = os.getenv("OPENROUTER_SITE_URL", "")
openrouter_site_name = os.getenv("OPENROUTER_SITE_NAME", "Jarvis Assistant")
openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-5.2")


def speak_old(text):
    engine.say(text)
    engine.runAndWait()
  
def speak(text):
    tts =gTTS(text)
    tts.save("temp.mp3")
    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load the MP3 file
    pygame.mixer.music.load('temp.mp3')

    # Play the MP3 file
    pygame.mixer.music.play()

    # Keep the program running until the music stops playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3") 

def aiProcess(command):
    if not openrouter_api_key:
        return "OPENROUTER_API_KEY missing hai. .env file mein key set karein."

    prompt = (
        "You are a virtual assistant named jarvis skilled in general tasks "
        "like Alexa and Google Cloud. Give short responses please.\n\n"
        f"User command: {command}"
    )

    openrouter_error = None
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openrouter_api_key}",
    }
    if openrouter_site_url:
        openrouter_headers["HTTP-Referer"] = openrouter_site_url
    if openrouter_site_name:
        openrouter_headers["X-OpenRouter-Title"] = openrouter_site_name

    openrouter_payload = {
        "model": openrouter_model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    try:
        print("Waiting for 15 seconds to avoid rate limit...")
        time.sleep(15)
        response = requests.post(
            openrouter_url,
            headers=openrouter_headers,
            data=json.dumps(openrouter_payload),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        choices = data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            if content:
                return content
        openrouter_error = "OpenRouter response format expected nahi tha."
    except requests.RequestException as e:
        openrouter_error = str(e)

    return f"OpenRouter request fail ho gayi: {openrouter_error}"



def process_command(c):
    if "open google" in c.lower():
        webbrowser.open("https://www.google.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com")
    elif "open instagram" in c.lower():
        webbrowser.open("https://www.instagram.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://www.linkedin.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://www.facebook.com")
    elif c.lower().startswith("play"):
        # extract the song name from the command and play it from the music library
        song = c.lower().split(" ")[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)
    elif "news" in c.lower():
        if not newsapi:
            speak("NEWS_API_KEY missing hai. .env file mein key set karein.")
            return

        r = requests.get(
            f"https://newsapi.org/v2/top-headlines?country=uk&apiKey={newsapi}",
            timeout=20,
        )
        if r.status_code == 200:
            
            #parse the JSON response
            data = r.json()
            
            #extract the headlines
            articles = data.get("articles", [])
            for article in articles:
                
                #print the headlines
                speak(article["title"])
                
    else:
        # Let OpenRouter handle the request
        output = aiProcess(c)
        speak(output)
               
if __name__ == "__main__":
    speak("Initialinzing Jarvis....")
    while True:
        #listen to the wake word "Jarvis"
        # obtain audio from the microphone
        r = sr.Recognizer()
        print("Recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening")
                audio = r.listen(source, timeout=2, phrase_time_limit=1)        
        # recognize speech using Google Speech Recognition
            word = r.recognize_google(audio)
            if(word.lower() == "jarvis"):
                speak("one one two two is activating")
                # listen for the next command
                with sr.Microphone() as source:
                    print("Jarvis Active...")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)
                    process_command(command)
        
        except Exception as e:
            print("Error; {0}".format(e))
