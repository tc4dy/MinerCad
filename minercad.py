# Developed by @tc4dy - Educational and Research Tool

import re
import sys
import json
import time
import socket
import threading
import requests
from queue import Queue
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

class LanguageManager:
    def __init__(self):
        self.lang = 'en'
        self.translations = {
            'banner': ('TACTICAL RECONNAISSANCE & INTELLIGENCE FRAMEWORK', 'TAKTİKSEL KEŞİF VE İSTİHBARAT SİSTEMİ'),
            'version': ('Version 3.0.0 - Ultimate OSINT Engine', 'Versiyon 3.0.0 - Ultimate OSINT Motoru'),
            'warning': ('LEGAL NOTICE: Authorized security research only', 'YASAL UYARI: Sadece yetkili güvenlik araştırmaları'),
            'lang_select': ('Select Language / Dil Seçin:\n[1] English\n[2] Türkçe\n> ', 'Select Language / Dil Seçin:\n[1] English\n[2] Türkçe\n> '),
            'target': ('Enter target domain (e.g., example.com): ', 'Hedef domaini girin (örn: example.com): '),
            'depth': ('Crawl depth (1-5, recommended: 2): ', 'Tarama derinliği (1-5, önerilen: 2): '),
            'threads': ('Thread count (1-20, recommended: 8): ', 'İş parçacığı sayısı (1-20, önerilen: 8): '),
            'timeout': ('Request timeout in seconds (5-30): ', 'İstek zaman aşımı saniye (5-30): '),
            'scanning': ('Initiating deep reconnaissance operations...', 'Derin keşif operasyonları başlatılıyor...'),
            'analyzing': ('Analyzing target infrastructure', 'Hedef altyapı analiz ediliyor'),
            'extracting': ('Extracting intelligence from sources', 'Kaynaklardan istihbarat çıkarılıyor'),
            'complete': ('Intelligence gathering completed successfully', 'İstihbarat toplama başarıyla tamamlandı'),
            'results': ('COMPREHENSIVE RECONNAISSANCE REPORT', 'KAPSAMLI KEŞİF RAPORU'),
            'duration': ('Total Duration', 'Toplam Süre'),
            'requests': ('HTTP Requests Made', 'Yapılan HTTP İstekleri'),
            'found': ('items found', 'öğe bulundu'),
            'menu': ('\n[1] New Scan  [2] Export JSON  [3] Export TXT  [4] Statistics  [5] Exit\n> ', 
                    '\n[1] Yeni Tarama  [2] JSON Aktar  [3] TXT Aktar  [4] İstatistikler  [5] Çıkış\n> '),
            'exported': ('Results exported to:', 'Sonuçlar aktarıldı:'),
            'stats': ('SCANNING STATISTICS', 'TARAMA İSTATİSTİKLERİ'),
            'processing': ('Processing', 'İşleniyor'),
        }
    
    def set_language(self, choice):
        self.lang = 'en' if choice == 1 else 'tr'
    
    def get(self, key):
        return self.translations.get(key, (key, key))[0 if self.lang == 'en' else 1]

class PatternExtractor:
    def __init__(self):
        self.patterns = {
            'emails': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            'phones': re.compile(r'\+?[0-9]{1,4}?[-.\s]?\(?[0-9]{1,3}?\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}'),
            'ipv4': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            'ipv6': re.compile(r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}'),
            'aws_keys': re.compile(r'AKIA[0-9A-Z]{16}'),
            'google_api': re.compile(r'AIza[0-9A-Za-z-_]{35}'),
            'firebase': re.compile(r'[a-z0-9-]+\.firebaseio\.com'),
            'stripe': re.compile(r'sk_live_[0-9a-zA-Z]{24}'),
            'ssh_key': re.compile(r'-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----'),
            'github_token': re.compile(r'ghp_[a-zA-Z0-9]{36}'),
            'jwt': re.compile(r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'),
            'credit_card': re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b'),
            'subdomains': re.compile(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}'),
            'urls': re.compile(r'https?://[^\s<>"\']+'),
            'social_media': re.compile(r'(?:https?://)?(?:www\.)?(?:twitter|facebook|linkedin|instagram|github|youtube|telegram|discord)\.(?:com|org)/[^\s<>"\']+'),
            'whatsapp': re.compile(r'(?:https?://)?(?:chat\.)?whatsapp\.com/[a-zA-Z0-9]+'),
            'discord_webhook': re.compile(r'https://discord(?:app)?\.com/api/webhooks/[0-9]+/[a-zA-Z0-9_-]+'),
            'telegram_bot': re.compile(r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}'),
            'sql_error': re.compile(r'(?:SQL syntax|mysql_fetch|Warning: mysql|PostgreSQL.*ERROR|ORA-[0-9]{5})'),
            'xss_vulnerable': re.compile(r'<script[^>]*>[^<]*(?:alert|prompt|confirm)\([^)]*\)[^<]*</script>'),
            'api_endpoints': re.compile(r'/api/v?[0-9]*/[a-zA-Z0-9/_-]+'),
            'env_vars': re.compile(r'(?:API_KEY|SECRET_KEY|PASSWORD|DB_PASS|TOKEN)=[^\s&]+'),
            'comments': re.compile(r'<!--[\s\S]*?-->'),
        }
        
        self.file_extensions = {
            'documents': ['.pdf', '.docx', '.xlsx', '.xls', '.doc', '.ppt', '.pptx'],
            'databases': ['.sql', '.db', '.sqlite', '.sqlite3', '.mdb', '.bkp', '.dump'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.iso', '.bz2'],
            'configs': ['.env', '.config', '.ini', '.yml', '.yaml', '.xml', '.json'],
            'scripts': ['.js', '.py', '.php', '.asp', '.jsp', '.sh', '.bash'],
            'vpn': ['.ovpn', '.conf'],
            'git': ['.git/config', '.gitignore', '.git/HEAD'],
        }
        
        self.technologies = {
            'WordPress': ['wp-content', 'wp-includes', 'wp-admin'],
            'Joomla': ['joomla', 'components/com_'],
            'Drupal': ['drupal', '/sites/default/'],
            'React': ['react', '_react', 'React.createElement'],
            'Vue.js': ['vue.js', 'Vue.component', '__vue__'],
            'Angular': ['angular', 'ng-app', 'ng-controller'],
            'jQuery': ['jquery', 'jQuery'],
            'Bootstrap': ['bootstrap.min', 'bootstrap.css'],
            'Laravel': ['laravel', 'laravel_session'],
            'Django': ['django', 'csrfmiddlewaretoken'],
            'Express': ['express', 'x-powered-by: Express'],
            'Flask': ['flask', 'werkzeug'],
            'Nginx': ['nginx', 'Server: nginx'],
            'Apache': ['apache', 'Server: Apache'],
            'Cloudflare': ['cloudflare', '__cfduid', 'cf-ray'],
            'Google Analytics': ['google-analytics', 'gtag', 'ga.js'],
            'Firebase': ['firebase', 'firebaseio'],
            'AWS': ['amazonaws.com', 's3.amazonaws'],
            'Docker': ['dockerfile', 'docker-compose'],
        }
    
    def extract_all(self, content, base_domain):
        results = defaultdict(set)
        
        for name, pattern in self.patterns.items():
            matches = pattern.findall(content.lower() if name in ['sql_error', 'xss_vulnerable'] else content)
            if name == 'subdomains':
                matches = [m for m in matches if base_domain in m and m != base_domain]
            if name == 'phones':
                matches = [m for m in matches if 10 <= len(re.sub(r'[^0-9]', '', m)) <= 20]
            results[name].update(matches)
        
        for category, extensions in self.file_extensions.items():
            for ext in extensions:
                if ext in content:
                    results[f'files_{category}'].add(ext)
        
        for tech, signatures in self.technologies.items():
            if any(sig.lower() in content.lower() for sig in signatures):
                results['technologies'].add(tech)
        
        return results

class WebCrawler:
    def __init__(self, depth=2, threads=8, timeout=10):
        self.depth = depth
        self.threads = threads
        self.timeout = timeout
        self.visited = set()
        self.lock = threading.Lock()
        self.results = defaultdict(set)
        self.request_count = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MinerCad/3.0 (Security Research; +https://github.com/tc4dy)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def normalize_url(self, url, base_url):
        if not url or url.startswith(('#', 'javascript:', 'mailto:')):
            return None
        if url.startswith('http'):
            return url
        return urljoin(base_url, url)
    
    def extract_links(self, content, base_url):
        links = set()
        for match in re.finditer(r'(?:href|src)=["\']([^"\']+)["\']', content):
            normalized = self.normalize_url(match.group(1), base_url)
            if normalized:
                links.add(normalized)
        return links
    
    def fetch(self, url):
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False, allow_redirects=True)
            self.request_count += 1
            return response.text, response.headers
        except:
            return None, None
    
    def crawl_url(self, url, depth, base_domain, extractor):
        if depth >= self.depth or url in self.visited:
            return
        
        with self.lock:
            if url in self.visited:
                return
            self.visited.add(url)
        
        content, headers = self.fetch(url)
        if not content:
            return
        
        extracted = extractor.extract_all(content, base_domain)
        with self.lock:
            for key, values in extracted.items():
                self.results[key].update(values)
            
            if headers:
                for header, value in headers.items():
                    self.results['http_headers'].add(f"{header}: {value}")
        
        if depth + 1 < self.depth:
            links = self.extract_links(content, url)
            domain_links = [link for link in links if base_domain in link]
            
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = [executor.submit(self.crawl_url, link, depth + 1, base_domain, extractor) 
                          for link in domain_links]
                for future in as_completed(futures):
                    pass
    
    def crawl(self, start_url, base_domain, lang_manager):
        extractor = PatternExtractor()
        print(f"\n\033[1;32m[◆]\033[0m {lang_manager.get('scanning')}")
        print(f"\033[1;32m[◆]\033[0m {lang_manager.get('analyzing')}")
        
        self.crawl_url(start_url, 0, base_domain, extractor)
        
        print(f"\033[1;32m[◆]\033[0m {lang_manager.get('extracting')}")
        return self.results, self.request_count

class ReportGenerator:
    def __init__(self, lang_manager):
        self.lang = lang_manager
    
    def print_console(self, data, domain, duration, requests):
        print("\n\n\033[1;35m" + "═" * 80 + "\033[0m")
        print(f"\033[1;35m  {self.lang.get('results')}\033[0m")
        print(f"\033[1;33m  Target: {domain}\033[0m")
        print("\033[1;35m" + "═" * 80 + "\033[0m\n")
        
        categories = {
            'AWS Keys': 'aws_keys',
            'Google API Keys': 'google_api',
            'Firebase URLs': 'firebase',
            'Stripe Keys': 'stripe',
            'SSH Private Keys': 'ssh_key',
            'GitHub Tokens': 'github_token',
            'JWT Tokens': 'jwt',
            'Credit Cards': 'credit_card',
            'Emails': 'emails',
            'Phone Numbers': 'phones',
            'IPv4 Addresses': 'ipv4',
            'IPv6 Addresses': 'ipv6',
            'Subdomains': 'subdomains',
            'Social Media': 'social_media',
            'WhatsApp Links': 'whatsapp',
            'Discord Webhooks': 'discord_webhook',
            'Telegram Bots': 'telegram_bot',
            'API Endpoints': 'api_endpoints',
            'SQL Errors': 'sql_error',
            'XSS Vulnerabilities': 'xss_vulnerable',
            'Environment Variables': 'env_vars',
            'Technologies': 'technologies',
            'PDF Documents': 'files_documents',
            'Databases': 'files_databases',
            'Archives': 'files_archives',
            'Config Files': 'files_configs',
            'Scripts': 'files_scripts',
            'VPN Files': 'files_vpn',
            'Git Files': 'files_git',
        }
        
        for category, key in categories.items():
            items = data.get(key, set())
            print(f"\033[1;36m▸ {category} ({len(items)}):\033[0m")
            if items:
                for i, item in enumerate(list(items)[:10]):
                    print(f"  \033[0;32m•\033[0m {item}")
                if len(items) > 10:
                    print(f"  \033[0;33m... and {len(items) - 10} more\033[0m")
            else:
                print("  \033[0;90m(none found)\033[0m")
            print()
        
        print("\033[1;35m" + "─" * 80 + "\033[0m")
        print(f"\033[1;32m✓ {self.lang.get('complete')}\033[0m")
        print(f"\033[1;36m  {self.lang.get('duration')}: {duration:.2f}s\033[0m")
        print(f"\033[1;36m  {self.lang.get('requests')}: {requests}\033[0m")
        print("\033[1;35m" + "═" * 80 + "\033[0m")
    
    def export_json(self, data, filename):
        serializable = {k: list(v) if isinstance(v, set) else v for k, v in data.items()}
        serializable['timestamp'] = datetime.now().isoformat()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
    
    def export_txt(self, data, filename, domain):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"MinerCad OSINT Report - {domain}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
            
            for category, items in data.items():
                f.write(f"\n[{category.upper()}] ({len(items)} items)\n")
                f.write("-" * 80 + "\n")
                for item in items:
                    f.write(f"{item}\n")

class MinerCad:
    def __init__(self):
        self.lang = LanguageManager()
        self.data = {}
        self.domain = ""
    
    def print_banner(self):
        print("\033[2J\033[1;1H\033[1;36m")
        print(r"""
    ███╗   ███╗██╗███╗   ██╗███████╗██████╗  ██████╗ █████╗ ██████╗ 
    ████╗ ████║██║████╗  ██║██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗
    ██╔████╔██║██║██╔██╗ ██║█████╗  ██████╔╝██║     ███████║██║  ██║
    ██║╚██╔╝██║██║██║╚██╗██║██╔══╝  ██╔══██╗██║     ██╔══██║██║  ██║
    ██║ ╚═╝ ██║██║██║ ╚████║███████╗██║  ██║╚██████╗██║  ██║██████╔╝
    ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝ 
        """)
        print("\033[0m\033[1;33m" + "═" * 80 + "\033[0m")
        print(f"\033[1;37m          {self.lang.get('banner')}\033[0m")
        print(f"\033[0;36m          {self.lang.get('version')}\033[0m")
        print("\033[1;33m" + "═" * 80 + "\033[0m")
        print(f"\033[1;31m  ⚠  {self.lang.get('warning')}  ⚠\033[0m")
        print("\033[1;33m" + "═" * 80 + "\033[0m\n")
    
    def scan(self, domain, depth, threads, timeout):
        self.domain = domain
        start_time = time.time()
        
        start_url = f"https://{domain}"
        crawler = WebCrawler(depth, threads, timeout)
        self.data, requests = crawler.crawl(start_url, domain, self.lang)
        
        duration = time.time() - start_time
        reporter = ReportGenerator(self.lang)
        reporter.print_console(self.data, domain, duration, requests)
    
    def run(self):
        try:
            choice = int(input(self.lang.get('lang_select')))
            self.lang.set_language(choice)
        except:
            self.lang.set_language(1)
        
        self.print_banner()
        
        while True:
            domain = input(f"\n\033[1;37m{self.lang.get('target')}\033[0m").strip()
            
            try:
                depth = int(input(f"\033[1;37m{self.lang.get('depth')}\033[0m"))
                depth = max(1, min(5, depth))
            except:
                depth = 2
            
            try:
                threads = int(input(f"\033[1;37m{self.lang.get('threads')}\033[0m"))
                threads = max(1, min(20, threads))
            except:
                threads = 8
            
            try:
                timeout = int(input(f"\033[1;37m{self.lang.get('timeout')}\033[0m"))
                timeout = max(5, min(30, timeout))
            except:
                timeout = 10
            
            self.scan(domain, depth, threads, timeout)
            
            try:
                choice = int(input(self.lang.get('menu')))
            except:
                choice = 5
            
            if choice == 5:
                break
            elif choice == 2:
                filename = f"minercad_{self.domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                ReportGenerator(self.lang).export_json(self.data, filename)
                print(f"\033[1;32m✓ {self.lang.get('exported')} {filename}\033[0m")
            elif choice == 3:
                filename = f"minercad_{self.domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                ReportGenerator(self.lang).export_txt(self.data, filename, self.domain)
                print(f"\033[1;32m✓ {self.lang.get('exported')} {filename}\033[0m")
            elif choice == 4:
                total = sum(len(v) for v in self.data.values())
                print(f"\n\033[1;35m{'═'*60}\033[0m")
                print(f"\033[1;35m  {self.lang.get('stats')}\033[0m")
                print(f"\033[1;35m{'═'*60}\033[0m")
                print(f"\033[1;36m  Total Data Points: {total}\033[0m")
                for category, items in sorted(self.data.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
                    print(f"\033[0;36m    - {category}: {len(items)}\033[0m")
                print(f"\033[1;35m{'═'*60}\033[0m")
            elif choice == 1:
                self.print_banner()

if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    engine = MinerCad()
    engine.run()