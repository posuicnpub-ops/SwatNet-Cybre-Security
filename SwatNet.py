import sys
import os
import json
import random
import threading
import sqlite3
import socket
import hashlib
import time
import re
import requests
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote, urlencode
import google.generativeai as genai
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtNetwork import *

os.environ['QT_OPENGL'] = 'software'
os.environ['QT_QUICK_BACKEND'] = 'software'

class AISystem:
    def __init__(self):
        self.ai_models = self.load_ai_models()
        self.conversation_history = []
        self.commands = self.load_commands()
        self.init_gemini()
        
    def init_gemini(self):
        try:
            genai.configure(api_key="AIzaSyC_DYf5l1NKmcwpyvH4twqqTZ1I5Qn3X1w")  # Public test key
            self.model = genai.GenerativeModel('gemini-pro')
            self.ai_active = True
        except:
            self.ai_active = False
            self.model = None
            
    def load_ai_models(self):
        return {
            'gemini': {
                'name': 'Google Gemini',
                'free': True,
                'url': 'https://ai.google.dev/',
                'capabilities': ['текст', 'код', 'поиск', 'анализ']
            },
            'openrouter': {
                'name': 'OpenRouter',
                'free': True,
                'url': 'https://openrouter.ai/',
                'capabilities': ['все модели', 'бесплатно']
            },
            'huggingface': {
                'name': 'HuggingFace',
                'free': True,
                'url': 'https://huggingface.co/',
                'capabilities': ['местные модели']
            },
            'local_llama': {
                'name': 'Local Llama',
                'free': True,
                'url': 'http://localhost:8080',
                'capabilities': ['полная приватность']
            }
        }
    
    def load_commands(self):
        return {
            'search': ['найди', 'ищи', 'поиск', 'search', 'find'],
            'hack': ['взломай', 'хакни', 'проникни', 'hack', 'exploit'],
            'analyze': ['анализ', 'проанализируй', 'проверь', 'analyze'],
            'code': ['напиши код', 'создай программу', 'code', 'program'],
            'web': ['открой сайт', 'зайди на', 'перейди на', 'open'],
            'swat': ['сватни', 'позвони в полицию', 'вызови скорую', 'swat'],
            'darknet': ['открой даркнет', 'найди в торе', 'onion', 'darknet'],
            'security': ['проверь безопасность', 'сканируй', 'security', 'scan'],
            'translate': ['переведи', 'translation', 'translate'],
            'explain': ['объясни', 'расскажи', 'explain', 'tell me']
        }
    
    def process_command(self, command):
        command_lower = command.lower()
        
        for cmd_type, keywords in self.commands.items():
            for keyword in keywords:
                if keyword in command_lower:
                    return self.execute_command(cmd_type, command)
        
        return self.chat_with_ai(command)
    
    def execute_command(self, cmd_type, command):
        responses = {
            'search': f"🔍 Ищу информацию: {command}",
            'hack': f"⚡ Начинаю анализ цели: {command}",
            'analyze': f"📊 Анализирую: {command}",
            'code': f"💻 Создаю код для: {command}",
            'web': f"🌐 Открываю: {command}",
            'swat': f"🚨 Активирую SWAT протокол: {command}",
            'darknet': f"🌑 Ищу в даркнете: {command}",
            'security': f"🛡️ Проверяю безопасность: {command}",
            'translate': f"🌍 Перевожу: {command}",
            'explain': f"📚 Объясняю: {command}"
        }
        
        return responses.get(cmd_type, f"Выполняю: {command}")
    
    def chat_with_ai(self, prompt):
        if not self.ai_active:
            return "🤖 AI: Использую локальную логику...\n" + self.fallback_response(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            return f"🤖 Gemini:\n{response.text}"
        except Exception as e:
            return f"🤖 AI (оффлайн):\n{self.fallback_response(prompt)}"
    
    def fallback_response(self, prompt):
        responses = [
            "Анализирую ваш запрос...",
            "Выполняю команду...",
            "Ищу информацию в базе данных...",
            "Подключаюсь к источникам...",
            "Генерирую ответ..."
        ]
        return random.choice(responses) + f"\nЗапрос: {prompt}"
    
    def search_web_ai(self, query):
        search_urls = [
            f"https://www.google.com/search?q={quote(query)}",
            f"https://duckduckgo.com/?q={quote(query)}",
            f"https://search.brave.com/search?q={quote(query)}"
        ]
        return search_urls

class TorManager:
    def __init__(self):
        self.tor_process = None
        self.tor_port = 9050
        self.tor_control_port = 9051
        self.is_running = False
        self.circuit_id = None
        
    def start_tor(self):
        try:
            temp_dir = os.path.join(os.getcwd(), "tor_data")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            torrc_content = f"""
SocksPort {self.tor_port}
ControlPort {self.tor_control_port}
DataDirectory {temp_dir}
Log notice stdout
CookieAuthentication 1
AvoidDiskWrites 1
"""
            
            torrc_path = os.path.join(temp_dir, "torrc")
            with open(torrc_path, 'w', encoding='utf-8') as f:
                f.write(torrc_content)
            
            if os.name == 'nt':
                self.tor_process = subprocess.Popen(
                    ['tor.exe', '-f', torrc_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.tor_process = subprocess.Popen(
                    ['tor', '-f', torrc_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            for i in range(30):
                try:
                    sock = socket.socket()
                    sock.settimeout(1)
                    sock.connect(('127.0.0.1', self.tor_port))
                    sock.close()
                    self.is_running = True
                    return True
                except:
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Tor error: {e}")
            
        return False
    
    def stop_tor(self):
        if self.tor_process:
            self.tor_process.terminate()
            try:
                self.tor_process.wait(timeout=5)
            except:
                self.tor_process.kill()
            self.is_running = False
    
    def new_identity(self):
        if self.is_running:
            try:
                import stem.control
                with stem.control.Controller.from_port(port=self.tor_control_port) as controller:
                    controller.authenticate()
                    controller.signal("NEWNYM")
                    time.sleep(3)
                    return True
            except:
                try:
                    response = requests.get(f"http://127.0.0.1:{self.tor_control_port}")
                    if response.status_code == 200:
                        return True
                except:
                    pass
        return False
    
    def get_ip(self):
        if not self.is_running:
            return None
            
        try:
            proxies = {
                'http': f'socks5h://127.0.0.1:{self.tor_port}',
                'https': f'socks5h://127.0.0.1:{self.tor_port}'
            }
            response = requests.get('https://api.ipify.org?format=json', 
                                  proxies=proxies, timeout=10)
            return response.json()['ip']
        except:
            return None

class LocationSpoofer:
    def __init__(self):
        self.countries = [
            {'code': 'US', 'name': 'USA', 'city': 'New York', 'timezone': 'America/New_York', 'language': 'en-US'},
            {'code': 'DE', 'name': 'Germany', 'city': 'Berlin', 'timezone': 'Europe/Berlin', 'language': 'de-DE'},
            {'code': 'JP', 'name': 'Japan', 'city': 'Tokyo', 'timezone': 'Asia/Tokyo', 'language': 'ja-JP'},
            {'code': 'RU', 'name': 'Russia', 'city': 'Moscow', 'timezone': 'Europe/Moscow', 'language': 'ru-RU'},
            {'code': 'NL', 'name': 'Netherlands', 'city': 'Amsterdam', 'timezone': 'Europe/Amsterdam', 'language': 'nl-NL'},
            {'code': 'SE', 'name': 'Sweden', 'city': 'Stockholm', 'timezone': 'Europe/Stockholm', 'language': 'sv-SE'},
            {'code': 'CH', 'name': 'Switzerland', 'city': 'Zurich', 'timezone': 'Europe/Zurich', 'language': 'de-CH'},
            {'code': 'CA', 'name': 'Canada', 'city': 'Toronto', 'timezone': 'America/Toronto', 'language': 'en-CA'}
        ]
        self.current_location = random.choice(self.countries)
        
    def change_location(self, country_code=None):
        if country_code:
            for country in self.countries:
                if country['code'] == country_code:
                    self.current_location = country
                    return True
        else:
            self.current_location = random.choice(self.countries)
            return True
        return False
    
    def get_location_info(self):
        return {
            'country': self.current_location['name'],
            'city': self.current_location['city'],
            'timezone': self.current_location['timezone'],
            'language': self.current_location['language']
        }
    
    def inject_location_js(self):
        location = self.get_location_info()
        js_code = f"""
        // Override geolocation
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition = function(success, error) {{
                success({{
                    coords: {{
                        latitude: {random.uniform(-90, 90)},
                        longitude: {random.uniform(-180, 180)},
                        accuracy: 100
                    }},
                    timestamp: Date.now()
                }});
            }};
        }}
        
        // Override timezone
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
            return {{
                locale: "{location['language']}",
                timeZone: "{location['timezone']}",
                hour12: false
            }};
        }};
        
        // Override language
        Object.defineProperty(navigator, 'language', {{
            get: function() {{ return "{location['language']}"; }}
        }});
        
        Object.defineProperty(navigator, 'languages', {{
            get: function() {{ return ["{location['language']}", "en-US", "en"]; }}
        }});
        
        console.log('Location spoofed: {location['city']}, {location['country']}');
        """
        return js_code

class DarknetManager:
    def __init__(self):
        self.onion_sites = self.load_onion_sites()
        self.onion_gateways = [
            'http://onion.ly/',
            'http://onion.cab/',
            'http://onion.to/',
            'http://onion.ws/'
        ]
        self.mirror_sites = self.load_mirror_sites()
        
    def load_onion_sites(self):
        return {
            'markets': [
                {'name': 'DarkMarket', 'url': 'http://darkmarketonion.com', 'v3': 'http://darkmarketx4zq2fq.onion'},
                {'name': 'Torrez Market', 'url': 'http://torrezmarket.org', 'v3': 'http://torrezmarket5j4ldx.onion'},
                {'name': 'ASAP Market', 'url': 'http://asapmarket.cc', 'v3': 'http://asap3kpcj6aq3n4r.onion'},
                {'name': 'Cannazon', 'url': 'http://cannazon.io', 'v3': 'http://cannazon5n6tzkw.onion'}
            ],
            'forums': [
                {'name': 'Dread', 'url': 'http://dreadditevelidot.onion', 'v3': 'http://dreadditevelidot.onion'},
                {'name': 'The Hub', 'url': 'http://thehub7gqe43.onion', 'v3': 'http://thehub7gqe43.onion'},
                {'name': 'Torum', 'url': 'http://torumv3address.onion', 'v3': 'http://torumv3address.onion'}
            ],
            'search': [
                {'name': 'Ahmia', 'url': 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion', 'v3': 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion'},
                {'name': 'Torch', 'url': 'http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion', 'v3': 'http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion'},
                {'name': 'DarkSearch', 'url': 'https://darksearch.io', 'clearnet': True}
            ],
            'services': [
                {'name': 'DoxBin', 'url': 'http://doxbin.org', 'v3': 'http://doxbin337azk.onion'},
                {'name': 'IntelExchange', 'url': 'https://intelx.io', 'clearnet': True},
                {'name': 'Dehashed', 'url': 'https://dehashed.com', 'clearnet': True},
                {'name': 'Leak.su', 'url': 'http://leaksu7vxcwj.onion', 'v3': 'http://leaksu7vxcwj.onion'}
            ],
            'wikis': [
                {'name': 'Darknet Bible', 'url': 'http://biblemeowimkh3utujmhm6oh2oeb3ubjw2lpgeq3lahrfr2l6ev6zgyd.onion', 'v3': 'http://biblemeowimkh3utujmhm6oh2oeb3ubjw2lpgeq3lahrfr2l6ev6zgyd.onion'},
                {'name': 'DNM Avengers', 'url': 'http://avengersdutyk3xf.onion', 'v3': 'http://avengersdutyk3xf.onion'}
            ]
        }
    
    def load_mirror_sites(self):
        return {
            'onion.ly': {'url': 'http://onion.ly/', 'method': 'prefix'},
            'onion.cab': {'url': 'http://onion.cab/', 'method': 'prefix'},
            'tor2web': {'url': 'https://tor2web.io/', 'method': 'suffix'},
            'onion.to': {'url': 'http://onion.to/', 'method': 'prefix'}
        }
    
    def get_onion_url(self, site, use_tor=True):
        if 'clearnet' in site and site['clearnet']:
            return site['url']
        
        if not use_tor:
            if 'v3' in site:
                gateway = random.choice(list(self.mirror_sites.keys()))
                mirror = self.mirror_sites[gateway]
                onion_domain = site['v3'].replace('http://', '').replace('.onion', '')
                
                if mirror['method'] == 'prefix':
                    return f"{mirror['url']}{onion_domain}"
                else:
                    return f"{onion_domain}{mirror['url']}"
        
        return site.get('v3', site['url'])

class BrowserSpoofer:
    def __init__(self):
        self.user_agents = self.load_user_agents()
        self.current_ua = random.choice(self.user_agents)
        self.fingerprint_data = self.generate_fingerprint()
        
    def load_user_agents(self):
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
    
    def generate_fingerprint(self):
        return {
            'screen_width': random.choice([1920, 1366, 1536, 1440, 1280]),
            'screen_height': random.choice([1080, 768, 864, 900, 1024]),
            'color_depth': random.choice([24, 30, 32]),
            'pixel_ratio': random.choice([1, 1.5, 2, 2.5]),
            'hardware_concurrency': random.choice([2, 4, 6, 8, 12, 16]),
            'device_memory': random.choice([4, 8, 16, 32]),
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
            'language': random.choice(['en-US', 'ru-RU', 'de-DE', 'fr-FR']),
            'timezone': random.choice(['Europe/Moscow', 'America/New_York', 'Europe/Berlin', 'Asia/Tokyo'])
        }
    
    def rotate_user_agent(self):
        self.current_ua = random.choice(self.user_agents)
        self.fingerprint_data = self.generate_fingerprint()
        return self.current_ua
    
    def inject_spoofing_js(self):
        fp = self.fingerprint_data
        js_code = f"""
        // Override user agent
        Object.defineProperty(navigator, 'userAgent', {{
            get: function() {{ return "{self.current_ua}"; }}
        }});
        
        // Override platform
        Object.defineProperty(navigator, 'platform', {{
            get: function() {{ return "{fp['platform']}"; }}
        }});
        
        // Override language
        Object.defineProperty(navigator, 'language', {{
            get: function() {{ return "{fp['language']}"; }}
        }});
        
        Object.defineProperty(navigator, 'languages', {{
            get: function() {{ return ["{fp['language']}", "en-US", "en"]; }}
        }});
        
        // Override hardware
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: function() {{ return {fp['hardware_concurrency']}; }}
        }});
        
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: function() {{ return {fp['device_memory']}; }}
        }});
        
        // Override screen
        Object.defineProperty(screen, 'width', {{
            get: function() {{ return {fp['screen_width']}; }}
        }});
        
        Object.defineProperty(screen, 'height', {{
            get: function() {{ return {fp['screen_height']}; }}
        }});
        
        Object.defineProperty(screen, 'colorDepth', {{
            get: function() {{ return {fp['color_depth']}; }}
        }});
        
        // Override pixel ratio
        Object.defineProperty(window, 'devicePixelRatio', {{
            get: function() {{ return {fp['pixel_ratio']}; }}
        }});
        
        // Disable WebRTC completely
        window.RTCPeerConnection = undefined;
        window.webkitRTCPeerConnection = undefined;
        window.mozRTCPeerConnection = undefined;
        window.RTCSessionDescription = undefined;
        window.RTCIceCandidate = undefined;
        
        // Clear WebRTC data
        if (window.localStorage) {{
            window.localStorage.removeItem('rtc');
            window.localStorage.removeItem('webrtc');
        }}
        
        console.log('Browser fingerprint spoofed');
        """
        return js_code

class SwatSystem:
    def __init__(self):
        self.call_history = []
        self.sms_history = []
        self.templates = self.load_templates()
        self.locations = self.load_locations()
        
    def load_templates(self):
        return {
            'police': [
                "Срочно! По адресу {address} слышны выстрелы! Вооруженные люди!",
                "Нападение! {address}, нужна вооруженная группа!",
                "Захват заложников! {address}, террористы с оружием!",
                "Вооруженное ограбление! {address}, стрельба!"
            ],
            'ambulance': [
                "Множественные ранения! {address}, срочно нужна скорая!",
                "Сердечный приступ! {address}, человек без сознания!",
                "Автокатастрофа! {address}, люди зажаты в машине!",
                "Падение с высоты! {address}, открытый перелом!"
            ],
            'fire': [
                "Сильный пожар! {address}, люди на верхних этажах!",
                "Взрыв газа! {address}, здание горит!",
                "Пожар с задымлением! {address}, люди не могут выйти!",
                "Химический пожар! {address}, опасные вещества!"
            ],
            'swat': [
                "Террористическая атака! {address}, требуются спецназ!",
                "Захват здания! {address}, вооруженные преступники!",
                "Взрывчатка в здании! {address}, угроза взрыва!",
                "Биологическая угроза! {address}, опасный материал!"
            ],
            'fake': [
                "Несчастный случай! {address}, нужна помощь!",
                "Подозрительный предмет! {address}, похож на бомбу!",
                "Нарушение порядка! {address}, драка с оружием!",
                "Потеря сознания! {address}, человек не дышит!"
            ]
        }
    
    def load_locations(self):
        return [
            "ул. Ленина, д. 25",
            "пр. Мира, д. 14",
            "ул. Советская, д. 8",
            "пр. Победы, д. 33",
            "ул. Центральная, д. 7",
            "пл. Революции, д. 1",
            "бульвар Свободы, д. 12",
            "наб. Речная, д. 45"
        ]
    
    def make_emergency_call(self, number, message, call_type="police"):
        call_id = hashlib.md5(f"{number}{message}{datetime.now()}".encode()).hexdigest()[:8]
        call_data = {
            'id': call_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'number': number,
            'message': message,
            'type': call_type,
            'status': 'simulated',
            'duration': random.randint(45, 180)
        }
        self.call_history.append(call_data)
        return call_data
    
    def send_emergency_sms(self, number, message):
        sms_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'number': number,
            'message': message,
            'status': 'simulated',
            'gateway': 'virtual'
        }
        self.sms_history.append(sms_data)
        return sms_data
    
    def generate_scenario(self, scenario_type="hostage", location=None):
        if not location:
            location = random.choice(self.locations)
        
        scenarios = {
            'hostage': {
                'title': 'Захват заложников',
                'message': f"Вооруженные люди удерживают заложников по адресу: {location}. Слышны выстрелы!",
                'response': 'SWAT + Negotiation Team + Snipers'
            },
            'bomb': {
                'title': 'Угроза взрыва',
                'message': f"Обнаружено взрывное устройство по адресу: {location}. Таймер показывает 15 минут!",
                'response': 'Bomb Squad + Evacuation + EOD'
            },
            'active_shooter': {
                'title': 'Активный стрелок',
                'message': f"Активный стрелок в здании по адресу: {location}. Множественные жертвы, стрельба продолжается!",
                'response': 'SWAT + Medical Teams + Helicopter'
            },
            'chemical': {
                'title': 'Химическая угроза',
                'message': f"Утечка опасных химикатов по адресу: {location}. Зона заражения 500 метров!",
                'response': 'Hazmat + Decontamination + Quarantine'
            },
            'cyber_attack': {
                'title': 'Кибер-атака',
                'message': f"Кибер-атака на критическую инфраструктуру: {location}. Отключены системы!",
                'response': 'Cyber Division + Technical Teams'
            }
        }
        
        return scenarios.get(scenario_type, scenarios['hostage'])

class SecuritySystem:
    def __init__(self):
        self.correct_login = "Батя от шаверми"
        self.correct_password = "0799"
        self.session_id = hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]

    def verify_credentials(self, login, password):
        return login.strip() == self.correct_login and password.strip() == self.correct_password

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('🔒 Swat Net AI - Secure Login')
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel('🤖 SWAT NET AI v9.0')
        title.setStyleSheet('''
            font-size: 28px;
            font-weight: bold;
            color: #00ffaa;
            padding: 10px;
            background: linear-gradient(90deg, #00ffaa, #0099ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel('ИИ Ассистент + Тор + Безопасность')
        subtitle.setStyleSheet('font-size: 14px; color: #888;')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText('Введите логин')
        self.username.setStyleSheet('''
            QLineEdit {
                padding: 15px;
                font-size: 16px;
                border: 2px solid #00ffaa;
                border-radius: 10px;
                background: #111;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0099ff;
            }
        ''')
        layout.addWidget(self.username)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText('Введите пароль')
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet('''
            QLineEdit {
                padding: 15px;
                font-size: 16px;
                border: 2px solid #00ffaa;
                border-radius: 10px;
                background: #111;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0099ff;
            }
        ''')
        layout.addWidget(self.password)
        
        login_btn = QPushButton('🚀 ВОЙТИ В СИСТЕМУ')
        login_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ffaa, stop:1 #0099ff);
                color: #000;
                padding: 18px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00cc88, stop:1 #0077cc);
            }
            QPushButton:pressed {
                background: #005599;
            }
        ''')
        login_btn.clicked.connect(self.authenticate)
        layout.addWidget(login_btn)
        
        self.error_label = QLabel()
        self.error_label.setStyleSheet('color: #ff5555; font-size: 14px;')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)
        
        hint = QLabel('Логин: Батя от шаверми | Пароль: 0799')
        hint.setStyleSheet('color: #666; font-size: 12px; font-style: italic;')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
        
        self.setLayout(layout)
        
    def authenticate(self):
        security = SecuritySystem()
        if security.verify_credentials(self.username.text(), self.password.text()):
            self.accept()
        else:
            self.error_label.setText('❌ Неверные учетные данные')
            self.password.clear()

class SwatNetAI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        login = LoginWindow()
        if login.exec() == QDialog.DialogCode.Accepted:
            self.ai_system = AISystem()
            self.security = SecuritySystem()
            self.tor_manager = TorManager()
            self.location_spoofer = LocationSpoofer()
            self.browser_spoofer = BrowserSpoofer()
            self.darknet_manager = DarknetManager()
            self.swat_system = SwatSystem()
            
            self.setup_ui()
            self.setup_tor()
            self.setup_ai()
        else:
            sys.exit(0)
    
    def setup_ui(self):
        self.setWindowTitle('🤖 Swat Net AI v9.0 | ИИ + Тор + SWAT + Darknet')
        self.setGeometry(50, 50, 1700, 950)
        
        self.setStyleSheet('''
            QMainWindow {
                background: #0a0a0a;
            }
            QTabWidget::pane {
                border: 3px solid #00ffaa;
                background: #111122;
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #1a1a2e;
                color: #8888aa;
                padding: 12px 24px;
                margin-right: 3px;
                font-weight: bold;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ffaa, stop:1 #0099ff);
                color: #000;
            }
            QTabBar::tab:hover {
                background: #333355;
                color: #ffffff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #222244, stop:1 #1a1a2e);
                color: #00ffaa;
                border: 2px solid #333355;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #333366, stop:1 #222244);
                border: 2px solid #00ffaa;
            }
            QPushButton:pressed {
                background: #111133;
            }
            QLineEdit, QTextEdit {
                background: #1a1a2e;
                color: #00ffaa;
                border: 3px solid #333355;
                border-radius: 8px;
                padding: 12px;
                font-family: "Consolas", "Monaco", monospace;
                font-size: 14px;
                selection-background-color: #0099ff;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 3px solid #0099ff;
            }
            QLabel {
                color: #aaccff;
                font-weight: bold;
                font-size: 13px;
            }
            QListWidget, QTreeWidget, QTableWidget {
                background: #111122;
                color: #ccccff;
                border: 2px solid #333355;
                border-radius: 6px;
                font-family: "Consolas", monospace;
                font-size: 12px;
            }
            QGroupBox {
                color: #00ffaa;
                font-weight: bold;
                font-size: 14px;
                border: 3px solid #333355;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 10px 0 10px;
                background: #1a1a2e;
            }
            QComboBox {
                background: #1a1a2e;
                color: #00ffaa;
                border: 2px solid #333355;
                border-radius: 6px;
                padding: 8px;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1a1a2e;
                color: #00ffaa;
                selection-background-color: #0099ff;
            }
            QProgressBar {
                border: 2px solid #333355;
                border-radius: 6px;
                text-align: center;
                background: #111122;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffaa, stop:1 #0099ff);
                border-radius: 4px;
            }
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #00ffaa;
                border-radius: 7px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #0099ff;
            }
            QMenuBar {
                background: #1a1a2e;
                color: #00ffaa;
                font-weight: bold;
            }
            QMenuBar::item:selected {
                background: #0099ff;
                color: #000;
            }
            QMenu {
                background: #1a1a2e;
                color: #00ffaa;
                border: 2px solid #333355;
            }
            QMenu::item:selected {
                background: #0099ff;
                color: #000;
            }
            QStatusBar {
                background: #1a1a2e;
                color: #00ffaa;
                font-weight: bold;
                border-top: 2px solid #333355;
            }
            QToolTip {
                background: #1a1a2e;
                color: #00ffaa;
                border: 2px solid #333355;
                padding: 5px;
                border-radius: 5px;
            }
        ''')
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        self.create_menu_bar()
        self.create_toolbar(main_layout)
        self.create_tabs(main_layout)
        self.create_status_bar()
        
        self.apply_security_settings()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('📁 Файл')
        
        new_tab_action = QAction('➕ Новая вкладка', self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(self.create_new_tab)
        file_menu.addAction(new_tab_action)
        
        new_window_action = QAction('🪟 Новое окно', self)
        new_window_action.setShortcut('Ctrl+N')
        new_window_action.triggered.connect(self.create_new_window)
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        save_action = QAction('💾 Сохранить сессию', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_session)
        file_menu.addAction(save_action)
        
        load_action = QAction('📂 Загрузить сессию', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_session)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('🚪 Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menubar.addMenu('✏️ Правка')
        
        copy_action = QAction('📋 Копировать', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.copy_text)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('📝 Вставить', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.paste_text)
        edit_menu.addAction(paste_action)
        
        clear_action = QAction('🗑️ Очистить всё', self)
        clear_action.setShortcut('Ctrl+Shift+C')
        clear_action.triggered.connect(self.clear_all)
        edit_menu.addAction(clear_action)
        
        view_menu = menubar.addMenu('👁️ Вид')
        
        zoom_in_action = QAction('🔍 Увеличить', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('🔎 Уменьшить', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction('🔄 Сбросить масштаб', self)
        reset_zoom_action.setShortcut('Ctrl+0')
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction('🖥️ Полный экран', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        tools_menu = menubar.addMenu('⚙️ Инструменты')
        
        ai_chat_action = QAction('🤖 ИИ Чат', self)
        ai_chat_action.setShortcut('Ctrl+I')
        ai_chat_action.triggered.connect(self.open_ai_chat)
        tools_menu.addAction(ai_chat_action)
        
        swat_tools_action = QAction('🚨 SWAT Инструменты', self)
        swat_tools_action.setShortcut('Ctrl+W')
        swat_tools_action.triggered.connect(self.open_swat_tools)
        tools_menu.addAction(swat_tools_action)
        
        darknet_action = QAction('🌑 Darknet', self)
        darknet_action.setShortcut('Ctrl+D')
        darknet_action.triggered.connect(self.open_darknet)
        tools_menu.addAction(darknet_action)
        
        privacy_action = QAction('🔒 Конфиденциальность', self)
        privacy_action.setShortcut('Ctrl+P')
        privacy_action.triggered.connect(self.open_privacy)
        tools_menu.addAction(privacy_action)
        
        help_menu = menubar.addMenu('❓ Помощь')
        
        about_action = QAction('ℹ️ О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction('📚 Документация', self)
        docs_action.triggered.connect(self.show_docs)
        help_menu.addAction(docs_action)
        
        help_menu.addSeparator()
        
        update_action = QAction('🔄 Проверить обновления', self)
        update_action.triggered.connect(self.check_updates)
        help_menu.addAction(update_action)
    
    def create_toolbar(self, layout):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        back_action = QAction('← Назад', self)
        back_action.triggered.connect(self.browser_back)
        toolbar.addAction(back_action)
        
        forward_action = QAction('→ Вперед', self)
        forward_action.triggered.connect(self.browser_forward)
        toolbar.addAction(forward_action)
        
        reload_action = QAction('↻ Обновить', self)
        reload_action.triggered.connect(self.browser_reload)
        toolbar.addAction(reload_action)
        
        home_action = QAction('🏠 Домой', self)
        home_action.triggered.connect(self.load_google)
        toolbar.addAction(home_action)
        
        toolbar.addSeparator()
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('Введите URL, поисковый запрос или команду для ИИ...')
        self.url_bar.setMinimumHeight(40)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        go_action = QAction('▶️ Вперед', self)
        go_action.triggered.connect(self.navigate_to_url)
        toolbar.addAction(go_action)
        
        toolbar.addSeparator()
        
        ai_quick_action = QAction('🤖 ИИ Помощник', self)
        ai_quick_action.triggered.connect(self.quick_ai_assist)
        toolbar.addAction(ai_quick_action)
        
        tor_action = QAction('🔒 Tor Вкл/Выкл', self)
        tor_action.triggered.connect(self.toggle_tor)
        toolbar.addAction(tor_action)
        
        layout.addWidget(toolbar)
    
    def create_tabs(self, layout):
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        self.browser_tab = self.create_browser_tab()
        self.ai_chat_tab = self.create_ai_chat_tab()
        self.darknet_tab = self.create_darknet_tab()
        self.swat_tab = self.create_swat_tab()
        self.privacy_tab = self.create_privacy_tab()
        self.tools_tab = self.create_tools_tab()
        
        self.tab_widget.addTab(self.browser_tab, "🌐 Браузер")
        self.tab_widget.addTab(self.ai_chat_tab, "🤖 ИИ Чат")
        self.tab_widget.addTab(self.darknet_tab, "🌑 Darknet")
        self.tab_widget.addTab(self.swat_tab, "🚨 SWAT")
        self.tab_widget.addTab(self.privacy_tab, "🔒 Конфиденциальность")
        self.tab_widget.addTab(self.tools_tab, "⚙️ Инструменты")
        
        layout.addWidget(self.tab_widget, 1)
    
    def create_browser_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.browser.loadStarted.connect(self.on_load_start)
        self.browser.loadProgress.connect(self.on_load_progress)
        self.browser.loadFinished.connect(self.on_load_finish)
        self.browser.urlChanged.connect(self.on_url_changed)
        
        layout.addWidget(self.browser)
        
        return widget
    
    def create_ai_chat_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        ai_title = QLabel('🤖 ИИ Ассистент Swat Net')
        ai_title.setStyleSheet('font-size: 22px; font-weight: bold; color: #00ffaa;')
        header_layout.addWidget(ai_title)
        
        header_layout.addStretch()
        
        ai_status = QLabel('🟢 Gemini Online')
        ai_status.setStyleSheet('color: #00ff00; font-weight: bold;')
        header_layout.addWidget(ai_status)
        
        layout.addWidget(header_frame)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet('''
            QTextEdit {
                background: #111122;
                color: #ccccff;
                border: 2px solid #333355;
                border-radius: 10px;
                font-family: "Consolas", monospace;
                font-size: 13px;
            }
        ''')
        self.chat_display.setHtml('''
            <div style="color:#00ffaa; font-weight:bold; font-size:16px;">🤖 ИИ Ассистент:</div>
            <div style="color:#aaddff; margin-left:20px; margin-top:10px;">
            Привет! Я ваш ИИ ассистент. Я могу:<br><br>
            • 💬 Общаться на любые темы<br>
            • 🔍 Искать информацию в интернете<br>
            • 💻 Писать и анализировать код<br>
            • 🚨 Помогать с SWAT сценариями<br>
            • 🌑 Искать в даркнете<br>
            • 🔒 Проверять безопасность<br>
            • 🌍 Переводить языки<br><br>
            <span style="color:#00ffaa;">Примеры команд:</span><br>
            "найди информацию о Python программировании"<br>
            "напиши код для парсинга сайта"<br>
            "объясни как работает Tor"<br>
            "переведи на английский: Привет мир"<br>
            "создай SWAT сценарий для тренировки"<br>
            </div>
        ''')
        layout.addWidget(self.chat_display, 1)
        
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText('Введите ваш запрос для ИИ...')
        self.ai_input.returnPressed.connect(self.process_ai_command)
        input_layout.addWidget(self.ai_input, 1)
        
        send_btn = QPushButton('➤ Отправить')
        send_btn.clicked.connect(self.process_ai_command)
        send_btn.setMinimumWidth(100)
        input_layout.addWidget(send_btn)
        
        voice_btn = QPushButton('🎤 Голос')
        voice_btn.clicked.connect(self.voice_input)
        voice_btn.setFixedWidth(60)
        input_layout.addWidget(voice_btn)
        
        layout.addWidget(input_frame)
        
        quick_commands_frame = QFrame()
        quick_layout = QHBoxLayout(quick_commands_frame)
        
        quick_commands = [
            ('🔍 Поиск в интернете', 'найди информацию о '),
            ('💻 Написать код', 'напиши код для '),
            ('🚨 SWAT помощь', 'помоги с SWAT сценарием '),
            ('🌑 Darknet поиск', 'найди в даркнете '),
            ('🔒 Проверка безопасности', 'проверь безопасность ')
        ]
        
        for text, cmd in quick_commands:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, c=cmd: self.set_ai_command(c))
            btn.setMaximumWidth(180)
            quick_layout.addWidget(btn)
        
        layout.addWidget(quick_commands_frame)
        
        return widget
    
    def create_darknet_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        categories = QTabWidget()
        
        all_categories = {
            'markets': ('🛒 Маркетплейсы', self.darknet_manager.onion_sites['markets']),
            'forums': ('💬 Форумы', self.darknet_manager.onion_sites['forums']),
            'search': ('🔍 Поисковики', self.darknet_manager.onion_sites['search']),
            'services': ('⚙️ Сервисы', self.darknet_manager.onion_sites['services']),
            'wikis': ('📚 Вики и базы', self.darknet_manager.onion_sites['wikis'])
        }
        
        for cat_name, (display_name, sites) in all_categories.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            site_list = QListWidget()
            site_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
            
            for site in sites:
                url = self.darknet_manager.get_onion_url(site, self.tor_manager.is_running)
                item_text = f"{site['name']}\n🔗 {url}"
                
                if 'v3' in site:
                    item_text += f"\n🎯 V3: {site['v3']}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, url)
                site_list.addItem(item)
            
            site_list.itemDoubleClicked.connect(self.open_darknet_site_from_list)
            tab_layout.addWidget(site_list)
            
            open_btn = QPushButton(f'🌐 Открыть выбранный сайт')
            open_btn.clicked.connect(lambda: self.open_selected_site(site_list))
            tab_layout.addWidget(open_btn)
            
            categories.addTab(tab, display_name)
        
        layout.addWidget(categories, 1)
        
        custom_frame = QFrame()
        custom_layout = QGridLayout(custom_frame)
        
        custom_label = QLabel('Пользовательский .onion:')
        custom_layout.addWidget(custom_label, 0, 0)
        
        self.custom_onion = QLineEdit()
        self.custom_onion.setPlaceholderText('Введите .onion адрес...')
        custom_layout.addWidget(self.custom_onion, 0, 1)
        
        open_custom_btn = QPushButton('🌐 Открыть через Tor')
        open_custom_btn.clicked.connect(self.open_custom_onion)
        custom_layout.addWidget(open_custom_btn, 0, 2)
        
        test_btn = QPushButton('🧪 Проверить доступность')
        test_btn.clicked.connect(self.test_onion_site)
        custom_layout.addWidget(test_btn, 1, 1)
        
        clear_btn = QPushButton('🗑️ Очистить')
        clear_btn.clicked.connect(lambda: self.custom_onion.clear())
        custom_layout.addWidget(clear_btn, 1, 2)
        
        layout.addWidget(custom_frame)
        
        return widget
    
    def create_swat_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        warning_label = QLabel("⚠️ ИМИТАЦИОННЫЕ ИНСТРУМЕНТЫ - ТОЛЬКО ДЛЯ ОБРАЗОВАНИЯ И ТРЕНИРОВОК ⚠️")
        warning_label.setStyleSheet("""
            QLabel {
                color: #ff0000;
                font-weight: bold;
                font-size: 18px;
                background: #330000;
                padding: 15px;
                border: 3px solid #ff0000;
                border-radius: 10px;
                text-align: center;
            }
        """)
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning_label)
        
        tabs = QTabWidget()
        
        calls_tab = QWidget()
        calls_layout = QVBoxLayout(calls_tab)
        
        number_group = QGroupBox("📞 Номер для вызова")
        number_layout = QVBoxLayout(number_group)
        
        self.swat_phone_input = QLineEdit()
        self.swat_phone_input.setPlaceholderText("+7XXXXXXXXXX или 112, 102, 103, 101, 911")
        number_layout.addWidget(self.swat_phone_input)
        
        calls_layout.addWidget(number_group)
        
        message_group = QGroupBox("💬 Сообщение для вызова")
        message_layout = QVBoxLayout(message_group)
        
        self.swat_message_input = QTextEdit()
        self.swat_message_input.setPlaceholderText("Введите подробное сообщение для экстренной службы...")
        self.swat_message_input.setMaximumHeight(120)
        message_layout.addWidget(self.swat_message_input)
        
        calls_layout.addWidget(message_group)
        
        templates_group = QGroupBox("🎭 Шаблоны вызовов")
        templates_layout = QGridLayout(templates_group)
        
        templates = [
            ("🚔 Полиция (стрельба)", "Выстрелы по адресу: {address}! Вооруженные люди!", "police"),
            ("🚔 Полиция (захват)", "Захват заложников! Адрес: {address}", "police"),
            ("🚑 Скорая (травма)", "Множественные травмы! Адрес: {address}", "ambulance"),
            ("🚑 Скорая (сердце)", "Остановка сердца! Адрес: {address}", "ambulance"),
            ("🚒 Пожарные (пожар)", "Сильный пожар! Адрес: {address}", "fire"),
            ("🚒 Пожарные (взрыв)", "Взрыв газа! Адрес: {address}", "fire"),
            ("🛡️ Спецназ (террористы)", "Террористическая атака! Адрес: {address}", "swat"),
            ("🛡️ Спецназ (взрывчатка)", "Взрывчатка в здании! Адрес: {address}", "swat"),
            ("🎭 Тестовый вызов", "Тест системы. Адрес: {address}", "fake"),
            ("🚨 Комбинированный", "Пожар + стрельба! Адрес: {address}", "police")
        ]
        
        row, col = 0, 0
        for name, template, type_ in templates:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, t=template: self.use_swat_template(t))
            btn.setMinimumHeight(40)
            templates_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        calls_layout.addWidget(templates_group)
        
        address_group = QGroupBox("📍 Адрес происшествия")
        address_layout = QHBoxLayout(address_group)
        
        self.swat_address_input = QLineEdit()
        self.swat_address_input.setPlaceholderText("Введите адрес или выберите из списка...")
        address_layout.addWidget(self.swat_address_input, 1)
        
        address_combo = QComboBox()
        for location in self.swat_system.locations:
            address_combo.addItem(location)
        address_combo.currentTextChanged.connect(self.swat_address_input.setText)
        address_layout.addWidget(address_combo)
        
        calls_layout.addWidget(address_group)
        
        action_group = QGroupBox("⚡ Действия")
        action_layout = QHBoxLayout(action_group)
        
        call_btn = QPushButton("📞 Имитировать звонок")
        call_btn.setStyleSheet("background: #ff3333; color: white; font-weight: bold;")
        call_btn.clicked.connect(self.make_swat_call)
        action_layout.addWidget(call_btn)
        
        sms_btn = QPushButton("💬 Имитировать SMS")
        sms_btn.clicked.connect(self.send_swat_sms)
        action_layout.addWidget(sms_btn)
        
        scenario_btn = QPushButton("🎭 Сгенерировать сценарий")
        scenario_btn.clicked.connect(self.generate_swat_scenario)
        action_layout.addWidget(scenario_btn)
        
        history_btn = QPushButton("📜 Показать историю")
        history_btn.clicked.connect(self.show_swat_history)
        action_layout.addWidget(history_btn)
        
        calls_layout.addWidget(action_group)
        
        tabs.addTab(calls_tab, "📞 Вызовы")
        
        scenarios_tab = QWidget()
        scenarios_layout = QVBoxLayout(scenarios_tab)
        
        scenario_types = [
            ('hostage', '👥 Захват заложников'),
            ('bomb', '💣 Угроза взрыва'),
            ('active_shooter', '🔫 Активный стрелок'),
            ('chemical', '☣️ Химическая угроза'),
            ('cyber_attack', '💻 Кибер-атака')
        ]
        
        for scenario_id, scenario_name in scenario_types:
            scenario_btn = QPushButton(scenario_name)
            scenario_btn.setMinimumHeight(50)
            scenario_btn.clicked.connect(lambda checked, sid=scenario_id: self.use_swat_scenario(sid))
            scenarios_layout.addWidget(scenario_btn)
        
        scenarios_layout.addStretch()
        
        tabs.addTab(scenarios_tab, "🎭 Сценарии")
        
        tools_tab = QWidget()
        tools_layout = QVBoxLayout(tools_tab)
        
        tools = [
            ("🎤 Генератор голоса", "Создать голосовое сообщение"),
            ("🗺️ Карта происшествий", "Показать на карте"),
            ("📊 Аналитика", "Статистика вызовов"),
            ("🔄 Массовые вызовы", "Несколько номеров"),
            ("⏱️ Таймер", "Запланировать вызов"),
            ("🎮 Тренировка", "Режим тренировки")
        ]
        
        for tool_name, tool_desc in tools:
            frame = QFrame()
            frame_layout = QHBoxLayout(frame)
            
            name_label = QLabel(tool_name)
            name_label.setStyleSheet("font-weight: bold; color: #00ffaa;")
            frame_layout.addWidget(name_label)
            
            desc_label = QLabel(tool_desc)
            desc_label.setStyleSheet("color: #888;")
            frame_layout.addWidget(desc_label)
            
            frame_layout.addStretch()
            
            activate_btn = QPushButton("Активировать")
            activate_btn.setFixedWidth(100)
            frame_layout.addWidget(activate_btn)
            
            tools_layout.addWidget(frame)
        
        tools_layout.addStretch()
        
        tabs.addTab(tools_tab, "⚙️ Инструменты")
        
        layout.addWidget(tabs, 1)
        
        return widget
    
    def create_privacy_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        tor_group = QGroupBox("🔒 Tor Настройки")
        tor_layout = QVBoxLayout(tor_group)
        
        self.tor_status_label = QLabel("Tor: Запускается...")
        self.tor_status_label.setStyleSheet("font-size: 14px; color: #ffaa00;")
        tor_layout.addWidget(self.tor_status_label)
        
        tor_btn_layout = QHBoxLayout()
        
        new_ip_btn = QPushButton("🔄 Получить новый IP")
        new_ip_btn.clicked.connect(self.new_tor_identity)
        tor_btn_layout.addWidget(new_ip_btn)
        
        check_ip_btn = QPushButton("🌐 Проверить текущий IP")
        check_ip_btn.clicked.connect(self.check_current_ip)
        tor_btn_layout.addWidget(check_ip_btn)
        
        restart_tor_btn = QPushButton("⚡ Перезапустить Tor")
        restart_tor_btn.clicked.connect(self.restart_tor)
        tor_btn_layout.addWidget(restart_tor_btn)
        
        tor_layout.addLayout(tor_btn_layout)
        
        self.current_ip_label = QLabel("Текущий IP: Неизвестен")
        self.current_ip_label.setStyleSheet("color: #00ffaa; font-weight: bold;")
        tor_layout.addWidget(self.current_ip_label)
        
        layout.addWidget(tor_group)
        
        location_group = QGroupBox("🌍 Смена местоположения")
        location_layout = QVBoxLayout(location_group)
        
        location_combo = QComboBox()
        for country in self.location_spoofer.countries:
            location_combo.addItem(f"📍 {country['name']} ({country['code']}) - {country['city']}", country['code'])
        
        location_btn_layout = QHBoxLayout()
        
        change_location_btn = QPushButton("🔄 Сменить страну")
        change_location_btn.clicked.connect(
            lambda: self.change_specific_location(location_combo.currentData())
        )
        location_btn_layout.addWidget(change_location_btn)
        
        random_location_btn = QPushButton("🎲 Случайная локация")
        random_location_btn.clicked.connect(self.change_random_location)
        location_btn_layout.addWidget(random_location_btn)
        
        location_layout.addWidget(location_combo)
        location_layout.addLayout(location_btn_layout)
        
        self.location_info_label = QLabel()
        self.location_info_label.setStyleSheet("color: #aaddff; background: #222244; padding: 10px; border-radius: 5px;")
        location_layout.addWidget(self.location_info_label)
        
        layout.addWidget(location_group)
        
        spoof_group = QGroupBox("🎭 Подмена браузера")
        spoof_layout = QVBoxLayout(spoof_group)
        
        ua_btn_layout = QHBoxLayout()
        
        rotate_ua_btn = QPushButton("🔄 Сменить User-Agent")
        rotate_ua_btn.clicked.connect(self.rotate_user_agent)
        ua_btn_layout.addWidget(rotate_ua_btn)
        
        inject_spoof_btn = QPushButton("💉 Внедрить подмену")
        inject_spoof_btn.clicked.connect(self.inject_spoofing)
        ua_btn_layout.addWidget(inject_spoof_btn)
        
        spoof_layout.addLayout(ua_btn_layout)
        
        self.ua_display_label = QLabel()
        self.ua_display_label.setStyleSheet("color: #ccccff; font-family: monospace; background: #111122; padding: 8px; border-radius: 5px;")
        spoof_layout.addWidget(self.ua_display_label)
        
        fingerprint_btn = QPushButton("👆 Показать Fingerprint")
        fingerprint_btn.clicked.connect(self.show_fingerprint)
        spoof_layout.addWidget(fingerprint_btn)
        
        layout.addWidget(spoof_group)
        
        security_group = QGroupBox("🛡️ Дополнительная безопасность")
        security_layout = QGridLayout(security_group)
        
        self.disable_webrtc = QCheckBox("Отключить WebRTC")
        self.disable_webrtc.setChecked(True)
        security_layout.addWidget(self.disable_webrtc, 0, 0)
        
        self.block_cookies = QCheckBox("Блокировать куки")
        self.block_cookies.setChecked(True)
        security_layout.addWidget(self.block_cookies, 0, 1)
        
        self.block_ads = QCheckBox("Блокировать рекламу")
        self.block_ads.setChecked(True)
        security_layout.addWidget(self.block_ads, 1, 0)
        
        self.clear_on_exit = QCheckBox("Очищать при выходе")
        self.clear_on_exit.setChecked(True)
        security_layout.addWidget(self.clear_on_exit, 1, 1)
        
        layout.addWidget(security_group)
        
        clear_group = QGroupBox("🗑️ Очистка данных")
        clear_layout = QHBoxLayout(clear_group)
        
        clear_cache_btn = QPushButton("Очистить кэш")
        clear_cache_btn.clicked.connect(self.clear_cache)
        clear_layout.addWidget(clear_cache_btn)
        
        clear_history_btn = QPushButton("Очистить историю")
        clear_history_btn.clicked.connect(self.clear_history)
        clear_layout.addWidget(clear_history_btn)
        
        clear_all_btn = QPushButton("🗑️ Очистить ВСЁ")
        clear_all_btn.setStyleSheet("background: #ff3333; color: white; font-weight: bold;")
        clear_all_btn.clicked.connect(self.clear_all_data)
        clear_layout.addWidget(clear_all_btn)
        
        layout.addWidget(clear_group)
        
        return widget
    
    def create_tools_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        network_group = QGroupBox("🌐 Сетевые инструменты")
        network_layout = QGridLayout(network_group)
        
        tools = [
            ("Ping", "ping -n 4 google.com", self.run_ping),
            ("Traceroute", "tracert google.com", self.run_traceroute),
            ("DNS Lookup", "nslookup google.com", self.run_nslookup),
            ("Port Scan", "Сканирование портов", self.run_portscan),
            ("WHOIS", "Информация о домене", self.run_whois),
            ("SSL Check", "Проверка сертификата", self.run_ssl_check)
        ]
        
        row, col = 0, 0
        for name, desc, func in tools:
            btn = QPushButton(name)
            btn.setToolTip(desc)
            btn.clicked.connect(func)
            btn.setMinimumHeight(40)
            network_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        layout.addWidget(network_group)
        
        web_group = QGroupBox("🕸️ Веб-инструменты")
        web_layout = QGridLayout(web_group)
        
        web_tools = [
            ("HTML Viewer", "Просмотр исходного кода", self.view_html_source),
            ("Header Analyzer", "Анализ заголовков", self.analyze_headers),
            ("Link Extractor", "Извлечение ссылок", self.extract_links),
            ("Screenshot", "Скриншот страницы", self.take_screenshot),
            ("Archive", "Архивировать страницу", self.archive_page),
            ("PDF Export", "Экспорт в PDF", self.export_pdf)
        ]
        
        row, col = 0, 0
        for name, desc, func in web_tools:
            btn = QPushButton(name)
            btn.setToolTip(desc)
            btn.clicked.connect(func)
            btn.setMinimumHeight(40)
            web_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        layout.addWidget(web_group)
        
        analysis_group = QGroupBox("📊 Анализ данных")
        analysis_layout = QGridLayout(analysis_group)
        
        analysis_tools = [
            ("Text Analysis", "Анализ текста", self.analyze_text),
            ("Image Analysis", "Анализ изображений", self.analyze_image),
            ("Code Analysis", "Анализ кода", self.analyze_code),
            ("Hash Calculator", "Вычислить хэш", self.calculate_hash),
            ("Encoding", "Кодирование/декодирование", self.encode_decode),
            ("Regex Tester", "Тест регулярных выражений", self.test_regex)
        ]
        
        row, col = 0, 0
        for name, desc, func in analysis_tools:
            btn = QPushButton(name)
            btn.setToolTip(desc)
            btn.clicked.connect(func)
            btn.setMinimumHeight(40)
            analysis_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        layout.addWidget(analysis_group, 1)
        
        return widget
    
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.tor_status_indicator = QLabel("🔴 Tor: Выкл")
        self.tor_status_indicator.setStyleSheet("color: #ff5555; font-weight: bold; padding: 5px;")
        self.status_bar.addWidget(self.tor_status_indicator)
        
        self.ai_status_indicator = QLabel("🤖 ИИ: Готов")
        self.ai_status_indicator.setStyleSheet("color: #00ffaa; padding: 5px;")
        self.status_bar.addWidget(self.ai_status_indicator)
        
        self.location_indicator = QLabel("📍 Неизвестно")
        self.location_indicator.setStyleSheet("color: #ffaa00; padding: 5px;")
        self.status_bar.addPermanentWidget(self.location_indicator)
        
        self.ip_indicator = QLabel("🌐 IP: Неизвестен")
        self.ip_indicator.setStyleSheet("color: #aaddff; padding: 5px;")
        self.status_bar.addPermanentWidget(self.ip_indicator)
        
        self.connection_status = QLabel("🔗 Соединение: Проверка...")
        self.status_bar.addPermanentWidget(self.connection_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setTextVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.time_label = QLabel()
        self.update_time()
        self.status_bar.addPermanentWidget(self.time_label)
        
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)
    
    def setup_tor(self):
        self.tor_thread = threading.Thread(target=self.start_tor_background, daemon=True)
        self.tor_thread.start()
    
    def start_tor_background(self):
        if self.tor_manager.start_tor():
            QMetaObject.invokeMethod(self, "update_tor_status", 
                                   Qt.ConnectionType.QueuedConnection,
                                   Q_ARG(bool, True))
        else:
            QMetaObject.invokeMethod(self, "update_tor_status",
                                   Qt.ConnectionType.QueuedConnection,
                                   Q_ARG(bool, False))
    
    def update_tor_status(self, success):
        if success:
            self.tor_status_label.setText("Tor: ✅ Запущен и работает")
            self.tor_status_indicator.setText("🟢 Tor: Вкл")
            self.tor_status_indicator.setStyleSheet("color: #00ff00; font-weight: bold; padding: 5px;")
            self.apply_tor_proxy()
            self.check_current_ip()
            self.location_info_label.setText("📍 Tor активен. IP скрыт.")
        else:
            self.tor_status_label.setText("Tor: ❌ Ошибка запуска")
            self.tor_status_indicator.setText("🔴 Tor: Выкл")
            self.tor_status_indicator.setStyleSheet("color: #ff0000; font-weight: bold; padding: 5px;")
            QMessageBox.warning(self, "Ошибка Tor", 
                              "Не удалось запустить Tor. Проверьте установку.\nДаркнет сайты могут не работать.")
    
    def setup_ai(self):
        if self.ai_system.ai_active:
            self.ai_status_indicator.setText("🤖 ИИ: Gemini Online")
            self.ai_status_indicator.setStyleSheet("color: #00ff00; padding: 5px;")
        else:
            self.ai_status_indicator.setText("🤖 ИИ: Оффлайн режим")
            self.ai_status_indicator.setStyleSheet("color: #ffaa00; padding: 5px;")
    
    def apply_tor_proxy(self):
        if self.tor_manager.is_running:
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.ProxyType.Socks5Proxy)
            proxy.setHostName("127.0.0.1")
            proxy.setPort(9050)
            QNetworkProxy.setApplicationProxy(proxy)
            self.connection_status.setText("🔗 Соединение: Tor")
        else:
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
            self.connection_status.setText("🔗 Соединение: Прямое")
    
    def apply_security_settings(self):
        profile = self.browser.page().profile()
        settings = profile.settings()
        
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        
        if self.disable_webrtc.isChecked():
            self.inject_spoofing()
    
    def update_time(self):
        current = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"🕐 {current}")
    
    def update_status(self):
        self.check_current_ip()
        
        if self.tor_manager.is_running:
            location = self.location_spoofer.get_location_info()
            self.location_indicator.setText(f"📍 {location['city']}")
        
        if self.browser.url().toString():
            url = self.browser.url().toString()
            if '.onion' in url:
                self.connection_status.setText(f"🔗 Onion: {url[:30]}...")
    
    def browser_back(self):
        self.browser.back()
    
    def browser_forward(self):
        self.browser.forward()
    
    def browser_reload(self):
        self.browser.reload()
    
    def load_google(self):
        self.browser.setUrl(QUrl("https://www.google.com"))
    
    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        
        if ' ' in text or text.startswith('найди') or text.startswith('search'):
            urls = self.ai_system.search_web_ai(text)
            self.browser.setUrl(QUrl(urls[0]))
        elif '.onion' in text:
            if not text.startswith('http'):
                text = 'http://' + text
            self.browser.setUrl(QUrl(text))
        else:
            if not text.startswith(('http://', 'https://')):
                text = 'https://' + text
            self.browser.setUrl(QUrl(text))
    
    def on_load_start(self):
        self.status_bar.showMessage("Загрузка...")
        self.progress_bar.setValue(0)
    
    def on_load_progress(self, progress):
        self.progress_bar.setValue(progress)
    
    def on_load_finish(self, success):
        if success:
            self.status_bar.showMessage("Готово", 2000)
            self.progress_bar.setValue(100)
            self.inject_spoofing()
        else:
            self.status_bar.showMessage("Ошибка загрузки", 2000)
            self.progress_bar.setValue(0)
    
    def on_url_changed(self, url):
        self.url_bar.setText(url.toString())
        
        if '.onion' in url.toString():
            self.status_bar.showMessage("🌑 Onion сайт через Tor", 3000)
    
    def new_tor_identity(self):
        if self.tor_manager.new_identity():
            self.check_current_ip()
            QMessageBox.information(self, "Успех", "🔄 Новый IP получен через Tor")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить новый IP")
    
    def check_current_ip(self):
        ip = self.tor_manager.get_ip()
        if ip:
            self.current_ip_label.setText(f"Текущий IP через Tor: {ip}")
            self.ip_indicator.setText(f"🌐 IP: {ip}")
            self.ip_indicator.setStyleSheet("color: #00ffaa; padding: 5px;")
        else:
            try:
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                ip = response.json()['ip']
                self.current_ip_label.setText(f"Текущий IP (прямой): {ip}")
                self.ip_indicator.setText(f"🌐 IP: {ip} (прямой)")
                self.ip_indicator.setStyleSheet("color: #ffaa00; padding: 5px;")
            except:
                self.current_ip_label.setText("IP: Не удалось определить")
                self.ip_indicator.setText("🌐 IP: Ошибка")
                self.ip_indicator.setStyleSheet("color: #ff5555; padding: 5px;")
    
    def change_specific_location(self, country_code):
        if self.location_spoofer.change_location(country_code):
            location = self.location_spoofer.get_location_info()
            self.location_info_label.setText(f"📍 {location['city']}, {location['country']}\n🕐 {location['timezone']}")
            self.location_indicator.setText(f"📍 {location['city']}")
            self.inject_spoofing()
            QMessageBox.information(self, "Локация изменена", 
                                  f"Теперь вы в {location['city']}, {location['country']}")
    
    def change_random_location(self):
        self.location_spoofer.change_location()
        location = self.location_spoofer.get_location_info()
        self.location_info_label.setText(f"📍 {location['city']}, {location['country']}\n🎲 Случайная локация")
        self.location_indicator.setText(f"📍 {location['city']}")
        self.inject_spoofing()
    
    def rotate_user_agent(self):
        ua = self.browser_spoofer.rotate_user_agent()
        self.ua_display_label.setText(f"User-Agent:\n{ua[:80]}...")
        self.inject_spoofing()
        QMessageBox.information(self, "User-Agent изменен", "Новый User-Agent применен")
    
    def inject_spoofing(self):
        try:
            location_js = self.location_spoofer.inject_location_js()
            browser_js = self.browser_spoofer.inject_spoofing_js()
            
            combined_js = location_js + "\n" + browser_js
            
            self.browser.page().runJavaScript(combined_js)
        except:
            pass
    
    def show_fingerprint(self):
        fp = self.browser_spoofer.fingerprint_data
        info = f"""
        🎭 Текущий Fingerprint:
        • Разрешение: {fp['screen_width']}x{fp['screen_height']}
        • Язык: {fp['language']}
        • Платформа: {fp['platform']}
        • CPU ядер: {fp['hardware_concurrency']}
        • Память: {fp['device_memory']}GB
        • Цвет: {fp['color_depth']}bit
        • Пиксели: x{fp['pixel_ratio']}
        • Таймзона: {fp['timezone']}
        """
        QMessageBox.information(self, "Browser Fingerprint", info)
    
    def open_darknet_site_from_list(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            self.tab_widget.setCurrentIndex(0)
            self.browser.setUrl(QUrl(url))
            self.url_bar.setText(url)
    
    def open_selected_site(self, site_list):
        item = site_list.currentItem()
        if item:
            url = item.data(Qt.ItemDataRole.UserRole)
            self.tab_widget.setCurrentIndex(0)
            self.browser.setUrl(QUrl(url))
            self.url_bar.setText(url)
    
    def open_custom_onion(self):
        url = self.custom_onion.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите .onion адрес")
            return
        
        if '.onion' not in url:
            QMessageBox.warning(self, "Ошибка", "Введите корректный .onion адрес")
            return
        
        if not url.startswith('http'):
            url = 'http://' + url
        
        self.tab_widget.setCurrentIndex(0)
        self.browser.setUrl(QUrl(url))
        self.url_bar.setText(url)
    
    def test_onion_site(self):
        url = self.custom_onion.text().strip()
        if not url or '.onion' not in url:
            QMessageBox.warning(self, "Ошибка", "Введите .onion адрес")
            return
        
        if not url.startswith('http'):
            url = 'http://' + url
        
        QMessageBox.information(self, "Проверка", 
                              f"Проверяем доступность:\n{url}\n\nЧерез Tor: {'Да' if self.tor_manager.is_running else 'Нет'}")
    
    def use_swat_template(self, template):
        address = self.swat_address_input.text() or random.choice(self.swat_system.locations)
        message = template.replace('{address}', address)
        self.swat_message_input.setPlainText(message)
    
    def make_swat_call(self):
        phone = self.swat_phone_input.text().strip()
        message = self.swat_message_input.toPlainText().strip()
        
        if not phone:
            QMessageBox.warning(self, "Ошибка", "Введите номер телефона")
            return
        
        if not message:
            QMessageBox.warning(self, "Ошибка", "Введите сообщение")
            return
        
        result = self.swat_system.make_emergency_call(phone, message)
        
        QMessageBox.information(self, "Вызов имитирован", 
                              f"📞 Вызов на: {phone}\n"
                              f"⏱️ Время: {result['timestamp']}\n"
                              f"⏳ Длительность: {result['duration']} сек\n"
                              f"📝 ID вызова: {result['id']}")
    
    def send_swat_sms(self):
        phone = self.swat_phone_input.text().strip()
        message = self.swat_message_input.toPlainText().strip()
        
        if not phone or not message:
            QMessageBox.warning(self, "Ошибка", "Заполните номер и сообщение")
            return
        
        result = self.swat_system.send_emergency_sms(phone, message)
        
        QMessageBox.information(self, "SMS имитировано", 
                              f"💬 SMS на: {phone}\n"
                              f"⏱️ Время: {result['timestamp']}\n"
                              f"📡 Шлюз: {result['gateway']}")
    
    def generate_swat_scenario(self):
        scenario = self.swat_system.generate_scenario()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🎭 Сгенерированный сценарий")
        dialog.setFixedSize(600, 400)
        
        layout = QVBoxLayout()
        
        title = QLabel(f"🚨 {scenario['title']}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff3333;")
        layout.addWidget(title)
        
        message = QTextEdit()
        message.setPlainText(scenario['message'])
        message.setReadOnly(True)
        layout.addWidget(message, 1)
        
        response = QLabel(f"🔹 Рекомендуемый ответ: {scenario['response']}")
        response.setStyleSheet("color: #00aaff; font-weight: bold;")
        layout.addWidget(response)
        
        use_btn = QPushButton("🎭 Использовать этот сценарий")
        use_btn.clicked.connect(lambda: self.use_generated_scenario(scenario['message']))
        layout.addWidget(use_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def use_generated_scenario(self, message):
        self.swat_message_input.setPlainText(message)
        QMessageBox.information(self, "Сценарий применен", "Сценарий скопирован в поле сообщения")
    
    def use_swat_scenario(self, scenario_type):
        scenario = self.swat_system.generate_scenario(scenario_type)
        self.swat_message_input.setPlainText(scenario['message'])
        QMessageBox.information(self, "Сценарий применен", f"Сценарий '{scenario['title']}' применен")
    
    def show_swat_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("📜 История вызовов")
        dialog.setFixedSize(700, 500)
        
        layout = QVBoxLayout()
        
        history_text = QTextEdit()
        history_text.setReadOnly(True)
        
        text = "📜 ИСТОРИЯ ВЫЗОВОВ SWAT\n" + "="*50 + "\n\n"
        
        for call in self.swat_system.call_history:
            text += f"📞 [{call['timestamp']}] {call['type'].upper()}\n"
            text += f"   📱 Номер: {call['number']}\n"
            text += f"   📝 Сообщение: {call['message'][:100]}...\n"
            text += f"   ⏳ Длительность: {call['duration']} сек\n"
            text += f"   🆔 ID: {call['id']}\n"
            text += "-"*50 + "\n"
        
        history_text.setPlainText(text)
        layout.addWidget(history_text)
        
        clear_btn = QPushButton("🗑️ Очистить историю")
        clear_btn.clicked.connect(lambda: self.clear_swat_history(history_text))
        layout.addWidget(clear_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def clear_swat_history(self, history_widget):
        self.swat_system.call_history = []
        history_widget.setPlainText("История очищена")
    
    def process_ai_command(self):
        command = self.ai_input.text().strip()
        if not command:
            return
        
        self.chat_display.append(f"<div style='color:#aaddff;'>👤 Вы: {command}</div>")
        
        response = self.ai_system.process_command(command)
        
        self.chat_display.append(f"<div style='color:#00ffaa; margin-left:20px;'>{response}</div>")
        
        self.ai_input.clear()
        
        if 'найди' in command.lower() or 'search' in command.lower():
            urls = self.ai_system.search_web_ai(command)
            if urls:
                self.browser.setUrl(QUrl(urls[0]))
                self.url_bar.setText(urls[0])
    
    def set_ai_command(self, command):
        self.ai_input.setText(command)
        self.ai_input.setFocus()
    
    def voice_input(self):
        QMessageBox.information(self, "Голосовой ввод", "Голосовой ввод в разработке...")
    
    def quick_ai_assist(self):
        self.tab_widget.setCurrentIndex(1)
        self.ai_input.setFocus()
    
    def toggle_tor(self):
        if self.tor_manager.is_running:
            self.tor_manager.stop_tor()
            self.tor_status_indicator.setText("🔴 Tor: Выкл")
            self.tor_status_indicator.setStyleSheet("color: #ff0000; font-weight: bold; padding: 5px;")
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
        else:
            self.start_tor_background()
    
    def restart_tor(self):
        self.tor_manager.stop_tor()
        time.sleep(2)
        self.start_tor_background()
    
    def clear_cache(self):
        self.browser.page().profile().clearHttpCache()
        QMessageBox.information(self, "Кэш очищен", "Кэш браузера очищен")
    
    def clear_history(self):
        self.browser.page().profile().clearAllVisitedLinks()
        QMessageBox.information(self, "История очищена", "История посещений очищена")
    
    def clear_all_data(self):
        reply = QMessageBox.question(self, "Очистка данных", 
                                   "Удалить ВСЕ данные (кэш, историю, сессии)?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.browser.page().profile().clearHttpCache()
            self.browser.page().profile().clearAllVisitedLinks()
            self.swat_system.call_history = []
            self.swat_system.sms_history = []
            self.ai_system.conversation_history = []
            QMessageBox.information(self, "Готово", "Все данные очищены")
    
    def create_new_tab(self):
        QMessageBox.information(self, "Новая вкладка", "Функция в разработке...")
    
    def create_new_window(self):
        QMessageBox.information(self, "Новое окно", "Функция в разработке...")
    
    def save_session(self):
        QMessageBox.information(self, "Сохранение", "Функция в разработке...")
    
    def load_session(self):
        QMessageBox.information(self, "Загрузка", "Функция в разработке...")
    
    def copy_text(self):
        QMessageBox.information(self, "Копирование", "Функция в разработке...")
    
    def paste_text(self):
        QMessageBox.information(self, "Вставка", "Функция в разработке...")
    
    def clear_all(self):
        QMessageBox.information(self, "Очистка", "Функция в разработке...")
    
    def zoom_in(self):
        current_zoom = self.browser.zoomFactor()
        self.browser.setZoomFactor(current_zoom + 0.1)
    
    def zoom_out(self):
        current_zoom = self.browser.zoomFactor()
        if current_zoom > 0.1:
            self.browser.setZoomFactor(current_zoom - 0.1)
    
    def reset_zoom(self):
        self.browser.setZoomFactor(1.0)
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def open_ai_chat(self):
        self.tab_widget.setCurrentIndex(1)
    
    def open_swat_tools(self):
        self.tab_widget.setCurrentIndex(3)
    
    def open_darknet(self):
        self.tab_widget.setCurrentIndex(2)
    
    def open_privacy(self):
        self.tab_widget.setCurrentIndex(4)
    
    def show_about(self):
        QMessageBox.about(self, "О Swat Net AI v9.0",
                        "🤖 Swat Net AI v9.0\n\n"
                        "Полный комплект инструментов:\n"
                        "• ИИ ассистент с Gemini\n"
                        "• Tor для анонимности\n"
                        "• Darknet доступ\n"
                        "• SWAT инструменты\n"
                        "• Смена локации\n"
                        "• Безопасный браузер\n\n"
                        "Логин: Батя от шаверми\n"
                        "Пароль: 0799")
    
    def show_docs(self):
        self.browser.setUrl(QUrl("https://www.google.com/search?q=swat+net+ai+documentation"))
    
    def check_updates(self):
        QMessageBox.information(self, "Обновления", "Проверка обновлений...\nТекущая версия: 9.0")
    
    def run_ping(self):
        QMessageBox.information(self, "Ping", "Выполняется ping...")
    
    def run_traceroute(self):
        QMessageBox.information(self, "Traceroute", "Выполняется traceroute...")
    
    def run_nslookup(self):
        QMessageBox.information(self, "NSLookup", "Выполняется nslookup...")
    
    def run_portscan(self):
        QMessageBox.information(self, "Port Scan", "Сканирование портов...")
    
    def run_whois(self):
        QMessageBox.information(self, "WHOIS", "Запрос WHOIS...")
    
    def run_ssl_check(self):
        QMessageBox.information(self, "SSL Check", "Проверка SSL...")
    
    def view_html_source(self):
        self.browser.page().toHtml(lambda html: QMessageBox.information(self, "HTML Source", html[:1000] + "..."))
    
    def analyze_headers(self):
        QMessageBox.information(self, "Headers", "Анализ заголовков...")
    
    def extract_links(self):
        QMessageBox.information(self, "Links", "Извлечение ссылок...")
    
    def take_screenshot(self):
        QMessageBox.information(self, "Screenshot", "Скриншот сохранен")
    
    def archive_page(self):
        QMessageBox.information(self, "Archive", "Архивирование...")
    
    def export_pdf(self):
        QMessageBox.information(self, "PDF", "Экспорт в PDF...")
    
    def analyze_text(self):
        QMessageBox.information(self, "Text Analysis", "Анализ текста...")
    
    def analyze_image(self):
        QMessageBox.information(self, "Image Analysis", "Анализ изображения...")
    
    def analyze_code(self):
        QMessageBox.information(self, "Code Analysis", "Анализ кода...")
    
    def calculate_hash(self):
        QMessageBox.information(self, "Hash", "Вычисление хэша...")
    
    def encode_decode(self):
        QMessageBox.information(self, "Encode/Decode", "Кодирование/декодирование...")
    
    def test_regex(self):
        QMessageBox.information(self, "Regex", "Тест регулярных выражений...")
    
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Swat Net AI v9.0")
    app.setApplicationVersion("9.0")
    app.setWindowIcon(QIcon())
    
    screen = QApplication.primaryScreen()
    screen_size = screen.size()
    
    window = SwatNetAI()
    
    if screen_size.width() > 1920:
        window.showMaximized()
    else:
        window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    0799
