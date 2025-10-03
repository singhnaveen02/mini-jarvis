import streamlit as st
import requests
import wikipedia
import datetime
import pyjokes
import yfinance as yf
from googletrans import Translator
import re
import math

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Mini Jarvis - AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------- CUSTOM STYLING --------------------
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #1f77b4;
    padding: 20px 0;
}
.chat-container {
    max-height: 400px;
    overflow-y: auto;
    padding: 20px;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    margin: 20px 0;
    background-color: #f9f9f9;
}
.voice-controls {
    text-align: center;
    padding: 20px;
}
.assistant-response {
    background-color: #e3f2fd;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #1f77b4;
}
.user-input {
    background-color: #f1f8e9;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #4caf50;
}
@media (max-width: 768px) {
    .main-container { padding: 10px; }
    .stButton > button { width: 100%; margin: 5px 0; }
}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "reminders" not in st.session_state:
    st.session_state.reminders = []

# -------------------- JARVIS CLASS --------------------
class WebJarvis:
    def __init__(self):
        self.weather_api_key = "a51eaca1954a256f122d4f1c8d4290b2"
        self.weather_base_url = "https://api.openweathermap.org/data/2.5/weather?"
        self.news_api_key = "YOUR_NEWS_API_KEY"  # Get from newsapi.org
        self.translator = Translator()
        st.info("💡 Enhanced Jarvis - Now with News, Stocks, Sports, Currency, Dictionary & More!")

    # ==================== EXISTING FEATURES ====================
    
    def get_weather(self, city_name: str) -> str:
        try:
            city_name = city_name.strip().replace(" ", "+")
            url = f"{self.weather_base_url}appid={self.weather_api_key}&q={city_name}&units=metric"
            response = requests.get(url)
            data = response.json()

            if int(data.get("cod", 404)) != 404:
                main = data["main"]
                weather_desc = data["weather"][0]["description"]
                return f"🌤️ {city_name}: {main['temp']}°C, {weather_desc}. Humidity {main['humidity']}%."
            else:
                return f"❌ Couldn't find weather for {city_name}. (Reason: {data.get('message')})"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def wikipedia_search(self, query: str) -> str:
        try:
            wikipedia.set_lang("en")
            return f"📚 {wikipedia.summary(query, sentences=2)}"
        except wikipedia.exceptions.DisambiguationError as e:
            return f"📚 {wikipedia.summary(e.options[0], sentences=2)}"
        except wikipedia.exceptions.PageError:
            return f"❌ No results found for '{query}'."
        except Exception:
            return "❌ Wikipedia search unavailable."

    def add_reminder(self, text: str) -> str:
        st.session_state.reminders.append({
            "text": text,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": False
        })
        return f"✅ Reminder added: {text}"

    def get_reminders(self) -> str:
        if not st.session_state.reminders:
            return "📝 You have no reminders."
        reminders = []
        for i, r in enumerate(st.session_state.reminders):
            status = "✓" if r.get("completed", False) else "○"
            reminders.append(f"{status} {i+1}. {r['text']} (Added: {r['created']})")
        return "📝 Your reminders:\n" + "\n".join(reminders)

    def get_time(self) -> str:
        return f"🕐 Current time: {datetime.datetime.now().strftime('%H:%M:%S')}"

    def get_date(self) -> str:
        return f"📅 Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}"

    def tell_joke(self) -> str:
        try:
            return f"😄 {pyjokes.get_joke()}"
        except:
            return "😄 Why don't scientists trust atoms? Because they make up everything!"

    # ==================== NEW FEATURES ====================
    
    # NEWS
    def get_news(self, category: str = "general") -> str:
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={self.news_api_key}"
            response = requests.get(url)
            data = response.json()
            
            if data.get("status") == "ok" and data.get("articles"):
                articles = data["articles"][:5]
                news_list = []
                for i, article in enumerate(articles, 1):
                    news_list.append(f"{i}. {article['title']}")
                return "📰 Top Headlines:\n" + "\n".join(news_list)
            else:
                return "❌ Unable to fetch news. Please check your API key."
        except Exception as e:
            return f"❌ News error: {str(e)}"

    # STOCK PRICES
    def get_stock_price(self, symbol: str) -> str:
        try:
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if current_price:
                company_name = info.get('longName', symbol)
                change = info.get('regularMarketChangePercent', 0)
                return f"💹 {company_name}\n💰 Price: ${current_price:.2f}\n📊 Change: {change:.2f}%"
            else:
                return f"❌ Could not find stock data for '{symbol}'"
        except Exception as e:
            return f"❌ Stock error: {str(e)}"

    # CRICKET/SPORTS SCORES (Using cricbuzz-like API)
    def get_cricket_score(self, team: str = "") -> str:
        try:
            # Using cricapi.com (requires API key) or alternative
            url = "https://api.cricapi.com/v1/currentMatches?apikey=YOUR_CRICKET_API_KEY"
            response = requests.get(url)
            data = response.json()
            
            if data.get("data"):
                matches = data["data"][:3]
                scores = []
                for match in matches:
                    scores.append(f"🏏 {match.get('name', 'Match')}: {match.get('status', 'Live')}")
                return "\n".join(scores) if scores else "🏏 No live matches at the moment."
            else:
                return "🏏 Cricket scores temporarily unavailable. (API key needed)"
        except Exception as e:
            return "🏏 Cricket scores temporarily unavailable."

    # CURRENCY CONVERTER
    def convert_currency(self, amount: float, from_curr: str, to_curr: str) -> str:
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}"
            response = requests.get(url)
            data = response.json()
            
            if to_curr.upper() in data.get("rates", {}):
                rate = data["rates"][to_curr.upper()]
                converted = amount * rate
                return f"💱 {amount} {from_curr.upper()} = {converted:.2f} {to_curr.upper()}"
            else:
                return f"❌ Currency '{to_curr}' not found."
        except Exception as e:
            return f"❌ Currency conversion error: {str(e)}"

    # DICTIONARY
    def get_meaning(self, word: str) -> str:
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url)
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                meaning = data[0]["meanings"][0]["definitions"][0]["definition"]
                return f"📖 {word.capitalize()}: {meaning}"
            else:
                return f"❌ No definition found for '{word}'"
        except Exception as e:
            return f"❌ Dictionary error: {str(e)}"

    # TRANSLATOR
    def translate_text(self, text: str, target_lang: str) -> str:
        try:
            translation = self.translator.translate(text, dest=target_lang)
            return f"🌐 Translation ({target_lang}): {translation.text}"
        except Exception as e:
            return f"❌ Translation error: {str(e)}"

    # CALCULATOR
    def calculate(self, expression: str) -> str:
        try:
            # Remove any potentially dangerous functions
            expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            result = eval(expression)
            return f"🧮 {expression} = {result}"
        except Exception as e:
            return f"❌ Calculation error. Use format: '23 + 45 / 7'"

    # TIMER
    def set_timer(self, minutes: int) -> str:
        if 'timers' not in st.session_state:
            st.session_state.timers = []
        
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        st.session_state.timers.append({
            "duration": minutes,
            "end_time": end_time.strftime("%H:%M:%S")
        })
        return f"⏰ Timer set for {minutes} minutes (ends at {end_time.strftime('%H:%M:%S')})"

    # UNIT CONVERTER
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> str:
        conversions = {
            # Distance
            ("km", "miles"): 0.621371,
            ("miles", "km"): 1.60934,
            ("m", "feet"): 3.28084,
            ("feet", "m"): 0.3048,
            # Weight
            ("kg", "lbs"): 2.20462,
            ("lbs", "kg"): 0.453592,
            # Temperature
            ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
            ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        }
        
        key = (from_unit.lower(), to_unit.lower())
        if key in conversions:
            factor = conversions[key]
            if callable(factor):
                result = factor(value)
            else:
                result = value * factor
            return f"📏 {value} {from_unit} = {result:.2f} {to_unit}"
        else:
            return f"❌ Conversion from {from_unit} to {to_unit} not supported."

    # TO-DO LIST
    def add_todo(self, task: str) -> str:
        if 'todos' not in st.session_state:
            st.session_state.todos = []
        
        st.session_state.todos.append({
            "task": task,
            "completed": False,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return f"✅ Task added: {task}"

    def get_todos(self) -> str:
        if 'todos' not in st.session_state or not st.session_state.todos:
            return "📋 Your to-do list is empty."
        
        todos = []
        for i, t in enumerate(st.session_state.todos, 1):
            status = "✓" if t["completed"] else "○"
            todos.append(f"{status} {i}. {t['task']}")
        return "📋 Your To-Do List:\n" + "\n".join(todos)

    def complete_todo(self, task_number: int) -> str:
        if 'todos' not in st.session_state or task_number > len(st.session_state.todos):
            return "❌ Invalid task number."
        
        st.session_state.todos[task_number - 1]["completed"] = True
        return f"✓ Task {task_number} marked as complete!"

    # ==================== COMMAND PROCESSOR ====================
    
    def process_command(self, command: str) -> str:
        command_lower = command.lower().strip()

        # Greetings
        if any(word in command_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            hour = datetime.datetime.now().hour
            greeting = "Good morning!" if 5 <= hour < 12 else "Good afternoon!" if 12 <= hour < 17 else "Good evening!"
            return f"👋 {greeting} I'm Enhanced Jarvis. How can I help?"

        # Time & Date
        if "time" in command_lower:
            return self.get_time()
        if "date" in command_lower or "today" in command_lower:
            return self.get_date()

        # Weather
        if "weather" in command_lower:
            if "in" in command_lower:
                city = command_lower.split("in")[-1].strip()
                return self.get_weather(city)
            return "🌤️ Please specify a city. Example: 'Weather in London'"

        # News
        if "news" in command_lower:
            return self.get_news()

        # Stock Prices
        if "stock" in command_lower or "share price" in command_lower:
            match = re.search(r'of\s+(\w+)', command_lower)
            if match:
                return self.get_stock_price(match.group(1))
            return "💹 Please specify a stock symbol. Example: 'Stock price of AAPL'"

        # Cricket Scores
        if "cricket" in command_lower or "score" in command_lower:
            return self.get_cricket_score()

        # Currency Converter
        if "convert" in command_lower and any(curr in command_lower for curr in ["usd", "inr", "eur", "gbp"]):
            match = re.search(r'(\d+\.?\d*)\s+(\w+)\s+to\s+(\w+)', command_lower)
            if match:
                amount, from_curr, to_curr = match.groups()
                return self.convert_currency(float(amount), from_curr, to_curr)
            return "💱 Format: 'Convert 100 USD to INR'"

        # Dictionary
        if "meaning" in command_lower or "define" in command_lower:
            word = command_lower.replace("meaning of", "").replace("define", "").strip()
            if word:
                return self.get_meaning(word)
            return "📖 What word should I define?"

        # Translator
        if "translate" in command_lower:
            match = re.search(r"'([^']+)'\s+to\s+(\w+)", command)
            if match:
                text, lang = match.groups()
                return self.translate_text(text, lang)
            return "🌐 Format: 'Translate 'hello' to Spanish'"

        # Calculator
        if "calculate" in command_lower or any(op in command for op in ["+", "-", "*", "/"]):
            expression = command_lower.replace("calculate", "").strip()
            return self.calculate(expression)

        # Timer
        if "timer" in command_lower:
            match = re.search(r'(\d+)\s+minute', command_lower)
            if match:
                return self.set_timer(int(match.group(1)))
            return "⏰ Format: 'Set a timer for 5 minutes'"

        # Unit Converter
        if "convert" in command_lower and any(unit in command_lower for unit in ["km", "miles", "kg", "lbs", "feet", "meter"]):
            match = re.search(r'(\d+\.?\d*)\s+(\w+)\s+to\s+(\w+)', command_lower)
            if match:
                value, from_unit, to_unit = match.groups()
                return self.convert_units(float(value), from_unit, to_unit)
            return "📏 Format: 'Convert 10 km to miles'"

        # To-Do List
        if "add task" in command_lower or "add todo" in command_lower:
            task = command_lower.replace("add task", "").replace("add todo", "").strip()
            if task:
                return self.add_todo(task)
            return "📋 What task should I add?"
        
        if "show tasks" in command_lower or "show todos" in command_lower or "todo list" in command_lower:
            return self.get_todos()
        
        if "complete task" in command_lower:
            match = re.search(r'(\d+)', command_lower)
            if match:
                return self.complete_todo(int(match.group(1)))
            return "📋 Which task number should I mark complete?"

        # Wikipedia
        if any(term in command_lower for term in ["search", "wikipedia", "tell me about", "what is", "who is"]):
            query = command_lower
            for term in ["search", "wikipedia", "tell me about", "what is", "who is"]:
                query = query.replace(term, "").strip()
            return self.wikipedia_search(query) if query else "🔍 What should I search for?"

        # Reminders
        if "remind me" in command_lower or "add reminder" in command_lower:
            text = command_lower.replace("remind me", "").replace("add reminder", "").strip()
            return self.add_reminder(text) if text else "📝 What should I remind you about?"
        if "reminders" in command_lower:
            return self.get_reminders()

        # Jokes
        if "joke" in command_lower or "funny" in command_lower:
            return self.tell_joke()

        # Help
        if "help" in command_lower:
            return """🤖 Enhanced Jarvis Commands:

📅 Time & Date → "What time is it?", "What's the date?"
🌤️ Weather → "Weather in [city]"
📰 News → "Latest news"
💹 Stocks → "Stock price of AAPL"
🏏 Cricket → "Cricket score"
💱 Currency → "Convert 100 USD to INR"
📖 Dictionary → "Meaning of serendipity"
🌐 Translate → "Translate 'hello' to Spanish"
🧮 Calculator → "Calculate 23 + 45 / 7"
⏰ Timer → "Set a timer for 5 minutes"
📏 Units → "Convert 10 km to miles"
📋 To-Do → "Add task buy groceries", "Show tasks", "Complete task 1"
🔍 Wikipedia → "Tell me about [topic]"
📝 Reminders → "Remind me to [task]", "Show reminders"
😄 Jokes → "Tell me a joke"
👋 Greetings → Say hello!"""

        return "🤔 I'm not sure. Try 'help' for available commands."


if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'todos' not in st.session_state:
    st.session_state.todos = []

# -------------------- INITIALIZE --------------------
jarvis = WebJarvis()

# -------------------- MAIN UI --------------------
st.markdown('<h1 class="main-header">🤖 Mini Jarvis</h1>', unsafe_allow_html=True)
# User input
user_input = st.text_input("💬 Type your message or command:", placeholder="Try: 'Hello', 'Weather in London'")

if st.button("🚀 Send Message") or user_input:
    if user_input:
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        st.session_state.chat_history.append({"role": "assistant", "message": jarvis.process_command(user_input)})

# Chat history
if st.session_state.chat_history:
    st.markdown("## 💭 Conversation")
    for chat in st.session_state.chat_history[-10:]:
        css_class = "user-input" if chat["role"] == "user" else "assistant-response"
        prefix = "You" if chat["role"] == "user" else "Jarvis"
        st.markdown(f'<div class="{css_class}"><strong>{prefix}:</strong> {chat["message"]}</div>', unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("🛠️ Features")

# Voice
st.sidebar.markdown("### 🎙️ Voice Input")
audio_bytes = st.sidebar.audio_input("Record your voice command")
if audio_bytes:
    st.sidebar.audio(audio_bytes, format="audio/wav")
    st.sidebar.success("🎵 Audio recorded!")
    st.sidebar.info("💡 Add speech_recognition for transcription")

# Quick actions
st.sidebar.markdown("### ⚡ Quick Actions")
if st.sidebar.button("🕐 Current Time"):
    st.session_state.chat_history.append({"role": "assistant", "message": jarvis.get_time()})
    st.rerun()
if st.sidebar.button("📅 Today's Date"):
    st.session_state.chat_history.append({"role": "assistant", "message": jarvis.get_date()})
    st.rerun()
if st.sidebar.button("😄 Tell a Joke"):
    st.session_state.chat_history.append({"role": "assistant", "message": jarvis.tell_joke()})
    st.rerun()
if st.sidebar.button("📝 Show Reminders"):
    st.session_state.chat_history.append({"role": "assistant", "message": jarvis.get_reminders()})
    st.rerun()
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()
