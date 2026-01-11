import speech_recognition as sr
import pyttsx3
import pywhatkit
import wikipedia
import datetime
import webbrowser
import os
import requests
from groq import Groq

# Initialize Groq client
# Get your API key from: https://console.groq.com/keys
GROQ_API_KEY = "enter your_groq_api_key_here"
client = Groq(api_key=GROQ_API_KEY)

# Weather API key
WEATHER_API_KEY = "enter your_openweathermap_api_key_here"

r = sr.Recognizer()
conversation_history = []

def speak(command):
    """Text to speech function"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 180)  # Speed of speech
    engine.say(command)
    engine.runAndWait()

def get_groq_response(user_input):
    """Get AI response from Groq API with web search capability"""
    try:
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Keep only last 10 messages to manage token usage
        messages_to_send = conversation_history[-10:]
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful voice assistant. Keep responses concise and conversational, under 100 words when possible. 
                    If asked about people, places, or current events you're unsure about, search the web for accurate information.
                    Always provide factual, up-to-date information."""
                }
            ] + messages_to_send,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300
        )
        
        response = chat_completion.choices[0].message.content
        conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "Sorry, I encountered an error processing your request."

def get_weather(city="Dhaka"):
    """Get weather information (requires OpenWeatherMap API key)"""
    api_key = WEATHER_API_KEY
    
    # Clean city name
    city = city.strip().title()
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        print(f"🌍 Fetching weather for: {city}")
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            temp = round(data['main']['temp'], 1)
            desc = data['weather'][0]['description']
            humidity = data['main']['humidity']
            feels_like = round(data['main']['feels_like'], 1)
            return f"The temperature in {city} is {temp} degrees Celsius, feels like {feels_like}. It's {desc} with {humidity} percent humidity."
        elif response.status_code == 401:
            return "Weather API key is not activated yet. It may take up to 2 hours after registration. Please try again later."
        elif response.status_code == 404:
            return f"Sorry, I couldn't find weather data for {city}. Please check the city name."
        else:
            data = response.json()
            error_msg = data.get('message', 'Unknown error')
            print(f"API Error: {error_msg}")
            return f"Sorry, weather service returned an error: {error_msg}"
            
    except requests.exceptions.Timeout:
        return "Weather service is taking too long to respond."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to weather service. Please check your internet connection."
    except Exception as e:
        print(f"Weather Error: {e}")
        return "An error occurred while fetching weather."

def search_wikipedia(query):
    """Enhanced Wikipedia search with better error handling"""
    try:
        print(f"📚 Searching Wikipedia for: {query}")
        # Set language to English
        wikipedia.set_lang("en")
        
        # Search for pages first to verify topic exists
        search_results = wikipedia.search(query, results=3)
        
        if not search_results:
            print("No Wikipedia results found")
            return None
        
        print(f"Found: {search_results[0]}")
        
        # Get summary of the most relevant result
        summary = wikipedia.summary(search_results[0], sentences=3, auto_suggest=False)
        return summary
        
    except wikipedia.exceptions.DisambiguationError as e:
        # Multiple results found, take the first one
        try:
            print(f"Multiple results found, using: {e.options[0]}")
            summary = wikipedia.summary(e.options[0], sentences=3, auto_suggest=False)
            return f"I found multiple results. Here's info about {e.options[0]}: {summary}"
        except:
            return None
            
    except wikipedia.exceptions.PageError:
        print("Page not found on Wikipedia")
        return None
        
    except Exception as e:
        print(f"Wikipedia Error: {e}")
        return None

def open_application(app_name):
    """Open common applications"""
    apps = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'chrome': 'chrome.exe',
        'browser': 'chrome.exe',
        'paint': 'mspaint.exe',
        'explorer': 'explorer.exe',
        'file explorer': 'explorer.exe',
        'command prompt': 'cmd.exe',
        'cmd': 'cmd.exe'
    }
    
    app_name = app_name.lower().strip()
    print(f"Trying to open: {app_name}")
    
    for key in apps:
        if key in app_name:
            try:
                os.system(apps[key])
                return f"Opening {key}"
            except Exception as e:
                print(f"Error opening {key}: {e}")
                return f"Could not open {key}"
    
    # Try to open as is
    try:
        os.system(f"start {app_name}")
        return f"Trying to open {app_name}"
    except:
        return f"Application '{app_name}' not found"

def test_weather_api():
    """Test if weather API is working"""
    print("\n" + "="*50)
    print("🧪 Testing Weather API...")
    print("="*50)
    
    result = get_weather("London")
    print(f"\nResult: {result}")
    
    if "not activated" in result:
        print("\n⚠️  Your API key needs activation (up to 2 hours)")
        print("   Check: https://home.openweathermap.org/api_keys")
    elif "error" in result.lower():
        print("\n❌ API Error detected")
    else:
        print("\n✅ Weather API is working!")
    
    print("="*50 + "\n")
    return result
    """Open common applications"""
    apps = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'chrome': 'chrome.exe',
        'browser': 'chrome.exe'
    }
    
    app_name = app_name.lower()
    for key in apps:
        if key in app_name:
            try:
                os.system(apps[key])
                return f"Opening {key}"
            except:
                return f"Could not open {key}"
    return "Application not found"

def search_web(query):
    """Search on Google"""
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching for {query} on Google"

def commands():
    """Main command processing function"""
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("\n🎤 Listening...")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            query = r.recognize_google(audio)
            query_lower = query.lower()
            print(f"You said: {query}")
            
            # Exit command
            if any(word in query_lower for word in ['exit', 'quit', 'goodbye', 'bye']):
                speak("Goodbye! Have a great day!")
                return False
            
            # Play YouTube videos
            elif 'play' in query_lower and 'youtube' in query_lower:
                song = query_lower.replace('play', '').replace('youtube', '').strip()
                speak(f'Playing {song} on YouTube')
                pywhatkit.playonyt(song)
            
            # Current date
            elif 'date' in query_lower or 'today' in query_lower:
                today = datetime.date.today().strftime('%B %d, %Y')
                speak(f'Today is {today}')
            
            # Current time
            elif 'time' in query_lower:
                now = datetime.datetime.now().strftime('%I:%M %p')
                speak(f'The time is {now}')
            
            # Wikipedia search
            elif 'wikipedia' in query_lower or 'who is' in query_lower or 'what is' in query_lower or 'tell me about' in query_lower or 'tell about' in query_lower:
                # Extract topic
                topic = query_lower
                for phrase in ['wikipedia', 'who is', 'what is', 'tell me about', 'tell about']:
                    topic = topic.replace(phrase, '')
                topic = topic.strip()
                
                if topic:
                    print(f"Topic extracted: '{topic}'")
                    
                    # Try Wikipedia first
                    wiki_result = search_wikipedia(topic)
                    
                    if wiki_result:
                        print(f"✅ Wikipedia found: {wiki_result[:100]}...")
                        speak(wiki_result)
                    else:
                        # Wikipedia failed, use Groq AI
                        print("⚠️ Wikipedia not found, asking AI...")
                        response = get_groq_response(f"Tell me about {topic}. Give a brief, factual answer in 2-3 sentences.")
                        print(f"🤖 AI Response: {response}")
                        speak(response)
                else:
                    speak("Please specify what you want to know about.")
            
            # Weather
            elif 'weather' in query_lower:
                city = "Dhaka"  # Default city
                # Better city extraction
                if 'in' in query_lower:
                    parts = query_lower.split('in')
                    if len(parts) > 1:
                        city = parts[-1].strip()
                        # Remove common words
                        city = city.replace('weather', '').replace('the', '').strip()
                elif 'for' in query_lower:
                    parts = query_lower.split('for')
                    if len(parts) > 1:
                        city = parts[-1].strip()
                        city = city.replace('weather', '').replace('the', '').strip()
                
                print(f"Extracted city: '{city}'")  # Debug line
                weather_info = get_weather(city)
                print(weather_info)
                speak(weather_info)
            
            # Open applications
            elif 'open' in query_lower:
                app = query_lower.replace('open', '').strip()
                result = open_application(app)
                speak(result)
            
            # Web search
            elif 'search' in query_lower or 'google' in query_lower:
                search_query = query_lower.replace('search', '').replace('google', '').strip()
                result = search_web(search_query)
                speak(result)
            
            # Send WhatsApp message (requires phone number)
            elif 'whatsapp' in query_lower:
                speak("What's the phone number?")
                # You'd need to implement number recognition here
                speak("Feature under development")
            
            # Groq AI response for everything else
            else:
                print("🤖 Getting AI response...")
                response = get_groq_response(query)
                print(f"Assistant: {response}")
                speak(response)
            
            return True
            
    except sr.WaitTimeoutError:
        print("⏱️ No speech detected, timeout.")
        return True
    except sr.UnknownValueError:
        print("❌ Sorry, I didn't catch that.")
        speak("Sorry, I didn't catch that. Could you please repeat?")
        return True
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return True

def main():
    """Main function to run the assistant"""
    print("=" * 50)
    print("🤖 AI Voice Assistant with Groq")
    print("=" * 50)
    
    # Test weather API first
    test_weather_api()
    
    print("\nAvailable Commands:")
    print("• 'play [song] on youtube' - Play videos")
    print("• 'what's the time/date' - Get time/date")
    print("• 'weather in [city]' - Get weather")
    print("• 'open [app]' - Open applications")
    print("• 'search [query]' - Google search")
    print("• 'who is/what is/tell about [topic]' - Get info")
    print("• Ask any question - AI will respond")
    print("• 'exit/quit/goodbye' - Close assistant")
    print("=" * 50)
    
    speak("Hello! I am your AI assistant powered by Groq. How can I help you today?")
    
    while True:
        if not commands():
            break

if __name__ == "__main__":
    main()