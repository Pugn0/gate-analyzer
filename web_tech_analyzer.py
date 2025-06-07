import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from urllib.parse import urlparse
from typing import Dict, List, Set, Optional, Any
import hashlib
import base64
from concurrent.futures import ThreadPoolExecutor
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebTechAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.technologies = self._load_technologies()
        self.categories = self._load_categories()
        self.cache = {}
        self.timeout = 10
        self.max_retries = 3
        self.concurrent_requests = 5
        
        # Palavras-chave adicionais para detecção de pagamentos
        self.payment_keywords = {
            'cartao': ['cartão', 'cartao', 'credit card', 'debit card', 'card payment', 'cartão de crédito', 'cartão de débito'],
            'boleto': ['boleto', 'bank slip', 'bank payment', 'boleto bancário'],
            'pix': ['pix', 'instant payment', 'qr code payment'],
            'transferencia': ['transferência', 'transferencia', 'bank transfer', 'wire transfer', 'débito em conta', 'debito em conta'],
            'parcelamento': ['parcelamento', 'installment', 'split payment'],
            'carteira': ['carteira digital', 'digital wallet', 'wallet'],
            'crypto': ['cryptocurrency', 'bitcoin', 'ethereum', 'crypto payment'],
            'gateway': ['payment gateway', 'gateway de pagamento', 'processador de pagamento']
        }
        
        # Padrões específicos para detecção de gateways
        self.gateway_patterns = {
            'MercadoPago': [
                'mercado pago',
                'mercadopago',
                'grupo mercado livre',
                'mercadolibre',
                'mp-checkout',
                'mp-button',
                'mp-sdk',
                'mp-scripts'
            ],
            'Wirecard': [
                'wirecard',
                'moip',
                'grupo wirecard',
                'wirecard ag',
                'moip-checkout',
                'moip-sdk',
                'moip-scripts'
            ],
            'PagSeguro': [
                'pagseguro',
                'grupo uol',
                'uol pagseguro',
                'ps-checkout',
                'ps-button',
                'ps-sdk',
                'ps-scripts'
            ],
            'PayPal': [
                'paypal',
                'paypal-checkout',
                'paypal-button',
                'paypal-sdk',
                'paypal-scripts',
                'paypal.com',
                'braintree'
            ],
            'Stripe': [
                'stripe',
                'stripe-checkout',
                'stripe-button',
                'stripe-sdk',
                'stripe-scripts',
                'stripe.com',
                'stripe-js',
                'stripe-payment'
            ],
            'VTEX': [
                'vtex',
                'vtex-checkout',
                'vtex-payment',
                'vtex.com.br',
                'vtex-sdk',
                'vtex-scripts'
            ],
            'Cielo': [
                'cielo',
                'cielo.com.br',
                'cielo-checkout',
                'cielo-payment',
                'cielo-sdk',
                'cielo-scripts',
                'cielo-api'
            ],
            'Rede': [
                'rede',
                'rede.com.br',
                'redecard',
                'rede-checkout',
                'rede-payment',
                'rede-sdk',
                'rede-scripts'
            ],
            'Stone': [
                'stone',
                'stone.com.br',
                'stone-payment',
                'stone-checkout',
                'stone-sdk',
                'stone-scripts',
                'stone-api'
            ],
            'GetNet': [
                'getnet',
                'getnet.com.br',
                'getnet-payment',
                'getnet-checkout',
                'getnet-sdk',
                'getnet-scripts'
            ],
            'Adyen': [
                'adyen',
                'adyen-checkout',
                'adyen-payment',
                'adyen-sdk',
                'adyen-scripts',
                'adyen.com'
            ],
            'Klarna': [
                'klarna',
                'klarna-checkout',
                'klarna-payment',
                'klarna-sdk',
                'klarna-scripts',
                'klarna.com'
            ],
            'Afterpay': [
                'afterpay',
                'afterpay-checkout',
                'afterpay-payment',
                'afterpay-sdk',
                'afterpay-scripts',
                'afterpay.com'
            ],
            'Affirm': [
                'affirm',
                'affirm-checkout',
                'affirm-payment',
                'affirm-sdk',
                'affirm-scripts',
                'affirm.com'
            ],
            'Vindi': [
                'vindi',
                'vindi-checkout',
                'vindi-payment',
                'vindi-sdk',
                'vindi-scripts',
                'vindi.com.br'
            ],
            'Ebanx': [
                'ebanx',
                'ebanx-checkout',
                'ebanx-payment',
                'ebanx-sdk',
                'ebanx-scripts',
                'ebanx.com'
            ],
            'Shopify Payments': [
                'shopify-payments',
                'shopify-payment',
                'shopify-checkout',
                'shopify-sdk',
                'shopify-scripts'
            ],
            'WooCommerce Payments': [
                'woocommerce-payments',
                'woocommerce-payment',
                'woocommerce-checkout',
                'woocommerce-sdk',
                'woocommerce-scripts'
            ],
            'Square': [
                'square',
                'square-payment',
                'square-checkout',
                'square-sdk',
                'square-scripts',
                'square.com'
            ],
            '2C2P': [
                '2c2p',
                '2c2p-payment',
                '2c2p-checkout',
                '2c2p-sdk',
                '2c2p-scripts'
            ],
            'PayU': [
                'payu',
                'payu-payment',
                'payu-checkout',
                'payu-sdk',
                'payu-scripts',
                'payu.com'
            ],
            'Rapyd': [
                'rapyd',
                'rapyd-payment',
                'rapyd-checkout',
                'rapyd-sdk',
                'rapyd-scripts',
                'rapyd.com'
            ],
            'Checkout.com': [
                'checkout.com',
                'checkout-payment',
                'checkout-checkout',
                'checkout-sdk',
                'checkout-scripts'
            ],
            'Payoneer': [
                'payoneer',
                'payoneer-payment',
                'payoneer-checkout',
                'payoneer-sdk',
                'payoneer-scripts',
                'payoneer.com'
            ],
            'TransferWise': [
                'transferwise',
                'wise-payment',
                'wise-checkout',
                'wise-sdk',
                'wise-scripts',
                'wise.com'
            ],
            'Revolut': [
                'revolut',
                'revolut-payment',
                'revolut-checkout',
                'revolut-sdk',
                'revolut-scripts',
                'revolut.com'
            ],
            'iZettle': [
                'izettle',
                'izettle-payment',
                'izettle-checkout',
                'izettle-sdk',
                'izettle-scripts',
                'izettle.com'
            ],
            'SumUp': [
                'sumup',
                'sumup-payment',
                'sumup-checkout',
                'sumup-sdk',
                'sumup-scripts',
                'sumup.com'
            ],
            'Paytm': [
                'paytm',
                'paytm-payment',
                'paytm-checkout',
                'paytm-sdk',
                'paytm-scripts',
                'paytm.com'
            ],
            'Razorpay': [
                'razorpay',
                'razorpay-payment',
                'razorpay-checkout',
                'razorpay-sdk',
                'razorpay-scripts',
                'razorpay.com'
            ],
            'PayStack': [
                'paystack',
                'paystack-payment',
                'paystack-checkout',
                'paystack-sdk',
                'paystack-scripts',
                'paystack.com'
            ],
            'Flutterwave': [
                'flutterwave',
                'flutterwave-payment',
                'flutterwave-checkout',
                'flutterwave-sdk',
                'flutterwave-scripts',
                'flutterwave.com'
            ],
            'M-Pesa': [
                'm-pesa',
                'mpesa',
                'mpesa-payment',
                'mpesa-checkout',
                'mpesa-sdk',
                'mpesa-scripts'
            ],
            'Alipay': [
                'alipay',
                'alipay-payment',
                'alipay-checkout',
                'alipay-sdk',
                'alipay-scripts',
                'alipay.com'
            ],
            'WeChat Pay': [
                'wechat-pay',
                'wechatpay',
                'wechat-payment',
                'wechat-checkout',
                'wechat-sdk',
                'wechat-scripts'
            ],
            'GrabPay': [
                'grabpay',
                'grab-pay',
                'grab-payment',
                'grab-checkout',
                'grab-sdk',
                'grab-scripts'
            ],
            'GoPay': [
                'gopay',
                'go-pay',
                'go-payment',
                'go-checkout',
                'go-sdk',
                'go-scripts'
            ],
            'OVO': [
                'ovo',
                'ovo-payment',
                'ovo-checkout',
                'ovo-sdk',
                'ovo-scripts'
            ],
            'DANA': [
                'dana',
                'dana-payment',
                'dana-checkout',
                'dana-sdk',
                'dana-scripts'
            ],
            'LinkAja': [
                'linkaja',
                'link-aja',
                'link-payment',
                'link-checkout',
                'link-sdk',
                'link-scripts'
            ],
            'QRIS': [
                'qris',
                'qris-payment',
                'qris-checkout',
                'qris-sdk',
                'qris-scripts'
            ]
        }

    def _load_technologies(self) -> Dict:
        """Carrega o banco de dados de tecnologias do arquivo JSON."""
        try:
            with open('technologies.json', 'r', encoding='utf-8') as f:
                return json.load(f)['technologies']
        except Exception as e:
            logger.error(f"Erro ao carregar banco de dados: {e}")
            return {}

    def _load_categories(self) -> Dict:
        """Carrega as categorias do arquivo JSON."""
        try:
            with open('categories.json', 'r', encoding='utf-8') as f:
                return json.load(f)['categories']
        except Exception as e:
            logger.error(f"Erro ao carregar categorias: {e}")
            return {}

    def _analyze_payment_keywords(self, text: str) -> Dict[str, List[str]]:
        """Analisa o texto em busca de palavras-chave relacionadas a pagamentos."""
        found_keywords = {}
        text = text.lower()
        
        for category, keywords in self.payment_keywords.items():
            found = []
            for keyword in keywords:
                if keyword.lower() in text:
                    found.append(keyword)
            if found:
                found_keywords[category] = found
                
        return found_keywords

    def _analyze_gateways(self, text: str, scripts: List[str]) -> Dict[str, Any]:
        """Analisa o texto e scripts em busca de gateways de pagamento."""
        found_gateways = {}
        text = text.lower()
        
        # Analisa o texto
        for gateway, patterns in self.gateway_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text:
                    found_gateways[gateway] = {
                        'confidence': 100,
                        'source': 'text'
                    }
                    break
        
        # Analisa os scripts
        for script in scripts:
            script = script.lower()
            for gateway, patterns in self.gateway_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in script:
                        found_gateways[gateway] = {
                            'confidence': 100,
                            'source': 'script'
                        }
                        break
        
        return found_gateways

    def analyze_url(self, url: str) -> Dict[str, Any]:
        """Analisa uma URL e retorna as tecnologias encontradas."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            # Verifica cache
            cache_key = hashlib.md5(url.encode()).hexdigest()
            if cache_key in self.cache:
                return self.cache[cache_key]

            # Faz a requisição HTTP
            response = self._make_request(url)
            if not response:
                return {'error': 'Falha ao acessar o site'}

            # Analisa o conteúdo
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Analisa palavras-chave de pagamento
            payment_keywords = self._analyze_payment_keywords(response.text)
            
            # Analisa gateways de pagamento
            gateways = self._analyze_gateways(
                response.text,
                [script.get('src', '') for script in soup.find_all('script', src=True)]
            )
            
            results = {
                'url': url,
                'technologies': self._analyze_technologies(response, soup),
                'server': self._analyze_server(response),
                'meta': self._extract_meta(soup),
                'cookies': self._analyze_cookies(response),
                'javascript': self._analyze_javascript(soup),
                'css': self._analyze_css(soup),
                'headers': dict(response.headers),
                'status_code': response.status_code,
                'payment_keywords': payment_keywords,
                'gateways': gateways
            }

            # Salva no cache
            self.cache[cache_key] = results
            return results

        except Exception as e:
            logger.error(f"Erro ao analisar {url}: {e}")
            return {'error': str(e)}

    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Faz uma requisição HTTP com retry."""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    verify=True,
                    allow_redirects=True
                )
                return response
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Falha na requisição para {url}: {e}")
                    return None
                time.sleep(1)

    def _analyze_technologies(self, response: requests.Response, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analisa todas as tecnologias possíveis no site."""
        found_techs = {}

        # Analisa headers
        for category, techs in self.technologies.items():
            for tech_name, tech_data in techs.items():
                if 'headers' in tech_data:
                    for header, pattern in tech_data['headers'].items():
                        if header in response.headers:
                            match = re.search(pattern, response.headers[header])
                            if match:
                                version = match.group(1) if len(match.groups()) > 0 else None
                                found_techs[tech_name] = {
                                    'category': category,
                                    'version': version,
                                    'confidence': 100,
                                    'description': tech_data.get('description', '')
                                }

        # Analisa scripts
        for script in soup.find_all('script'):
            src = script.get('src', '')
            content = script.string or ''
            
            for category, techs in self.technologies.items():
                for tech_name, tech_data in techs.items():
                    if 'scriptSrc' in tech_data:
                        for pattern in tech_data['scriptSrc']:
                            if re.search(pattern, src, re.I):
                                found_techs[tech_name] = {
                                    'category': category,
                                    'confidence': 100,
                                    'description': tech_data.get('description', '')
                                }

        # Analisa meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            for category, techs in self.technologies.items():
                for tech_name, tech_data in techs.items():
                    if 'meta' in tech_data:
                        for meta_name, pattern in tech_data['meta'].items():
                            if meta_name.lower() == name:
                                match = re.search(pattern, content)
                                if match:
                                    version = match.group(1) if len(match.groups()) > 0 else None
                                    found_techs[tech_name] = {
                                        'category': category,
                                        'version': version,
                                        'confidence': 100,
                                        'description': tech_data.get('description', '')
                                    }

        # Analisa cookies
        for category, techs in self.technologies.items():
            for tech_name, tech_data in techs.items():
                if 'cookies' in tech_data:
                    for cookie_name, pattern in tech_data['cookies'].items():
                        for cookie in response.cookies:
                            if re.search(cookie_name, cookie.name):
                                found_techs[tech_name] = {
                                    'category': category,
                                    'confidence': 100,
                                    'description': tech_data.get('description', '')
                                }

        return found_techs

    def _analyze_server(self, response: requests.Response) -> Dict[str, Any]:
        """Analisa informações do servidor."""
        server_info = {}
        
        # Server header
        if 'Server' in response.headers:
            server_info['server'] = response.headers['Server']
        
        # X-Powered-By header
        if 'X-Powered-By' in response.headers:
            server_info['powered_by'] = response.headers['X-Powered-By']
        
        return server_info

    def _extract_meta(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrai informações das meta tags."""
        meta_info = {}
        
        # Generator
        generator = soup.find('meta', {'name': 'generator'})
        if generator:
            meta_info['generator'] = generator.get('content')
        
        # Description
        description = soup.find('meta', {'name': 'description'})
        if description:
            meta_info['description'] = description.get('content')
        
        # Keywords
        keywords = soup.find('meta', {'name': 'keywords'})
        if keywords:
            meta_info['keywords'] = keywords.get('content')
        
        return meta_info

    def _analyze_cookies(self, response: requests.Response) -> Dict[str, Any]:
        """Analisa os cookies do site."""
        cookies = {}
        for cookie in response.cookies:
            cookies[cookie.name] = {
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'expires': cookie.expires,
                'secure': cookie.secure,
                'httponly': cookie.has_nonstandard_attr('HttpOnly')
            }
        return cookies

    def _analyze_javascript(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analisa scripts JavaScript."""
        js_info = {
            'inline_scripts': [],
            'external_scripts': []
        }
        
        for script in soup.find_all('script'):
            if script.get('src'):
                js_info['external_scripts'].append(script['src'])
            elif script.string:
                js_info['inline_scripts'].append(script.string.strip())
        
        return js_info

    def _analyze_css(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analisa arquivos CSS."""
        css_info = {
            'external_stylesheets': [],
            'inline_styles': []
        }
        
        # External stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                css_info['external_stylesheets'].append(link['href'])
        
        # Inline styles
        for style in soup.find_all('style'):
            if style.string:
                css_info['inline_styles'].append(style.string.strip())
        
        return css_info

    def analyze_multiple_urls(self, urls: List[str]) -> Dict[str, Dict]:
        """Analisa múltiplas URLs em paralelo."""
        results = {}
        with ThreadPoolExecutor(max_workers=self.concurrent_requests) as executor:
            future_to_url = {executor.submit(self.analyze_url, url): url for url in urls}
            for future in future_to_url:
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    results[url] = {'error': str(e)}
        return results

def main():
    analyzer = WebTechAnalyzer()
    
    print("=== Analisador de Tecnologias Web ===")
    print("Cole a URL do site que deseja analisar (ex: google.com)")
    print("Digite 'sair' para encerrar")
    
    while True:
        url = input("\nURL: ").strip()
        
        if url.lower() == 'sair':
            break
            
        if not url:
            print("Por favor, digite uma URL válida")
            continue
            
        print("\nAnalisando...")
        result = analyzer.analyze_url(url)
        
        if 'error' in result:
            print(f"\nErro: {result['error']}")
            continue
            
        print("\n=== Resultados da Análise ===")
        print(f"URL: {result['url']}")
        print(f"Status: {result['status_code']}")
        
        # Mostra os gateways de pagamento encontrados
        print("\n=== Gateways de Pagamento ===")
        if result.get('gateways'):
            for gateway, info in result['gateways'].items():
                print(f"- {gateway}")
                if info.get('version'):
                    print(f"  Versão: {info['version']}")
                if info.get('description'):
                    print(f"  Descrição: {info['description']}")
        else:
            print("Nenhum gateway de pagamento encontrado")
        
        # Mostra formas de pagamento em uma única linha
        if result.get('payment_keywords'):
            print("\n=== Formas de Pagamento Disponíveis ===")
            payment_methods = []
            
            # Mapeia as categorias para nomes mais amigáveis
            category_names = {
                'cartao': 'Cartão',
                'boleto': 'Boleto',
                'pix': 'Pix',
                'transferencia': 'Transferência',
                'parcelamento': 'Parcelamento',
                'carteira': 'Carteira Digital',
                'crypto': 'Criptomoedas'
            }
            
            for category, keywords in result['payment_keywords'].items():
                if category in category_names:
                    payment_methods.append(category_names[category])
            
            if payment_methods:
                print("Métodos: " + ", ".join(payment_methods))
            else:
                print("Nenhum método de pagamento encontrado")
        
        # Mostra todas as tecnologias relevantes
        print("\n=== Tecnologias Encontradas ===")
        
        # Categorias e suas descrições
        categories = {
            'security': 'Segurança',
            'frameworks': 'Frameworks',
            'cms': 'Sistema de Gerenciamento de Conteúdo',
            'servers': 'Servidores',
            'analytics': 'Analytics',
            'widgets': 'Widgets',
            'marketing': 'Marketing',
            'payment': 'Pagamento',
            'hosting': 'Hospedagem',
            'cdn': 'CDN',
            'caching': 'Cache',
            'database': 'Banco de Dados',
            'programming': 'Linguagens de Programação',
            'web_servers': 'Servidores Web',
            'web_frameworks': 'Frameworks Web',
            'javascript_frameworks': 'Frameworks JavaScript',
            'ui_frameworks': 'Frameworks de UI',
            'mobile_frameworks': 'Frameworks Mobile',
            'rich_text_editors': 'Editores de Texto Rico',
            'tag_managers': 'Gerenciadores de Tags',
            'advertising': 'Publicidade',
            'live_chat': 'Chat ao Vivo',
            'social': 'Redes Sociais',
            'ecommerce': 'E-commerce',
            'cms': 'CMS',
            'message_boards': 'Fóruns',
            'documentation_systems': 'Sistemas de Documentação',
            'widgets': 'Widgets',
            'rich_text_editors': 'Editores de Texto Rico',
            'development': 'Desenvolvimento',
            'lms': 'Sistemas de Gestão de Aprendizagem',
            'web_servers': 'Servidores Web',
            'web_frameworks': 'Frameworks Web',
            'analytics': 'Analytics',
            'blogs': 'Blogs',
            'javascript_frameworks': 'Frameworks JavaScript',
            'issue_trackers': 'Rastreadores de Problemas',
            'video_players': 'Players de Vídeo',
            'comment_systems': 'Sistemas de Comentários',
            'security': 'Segurança',
            'advertising': 'Publicidade',
            'cdn': 'CDN',
            'tag_managers': 'Gerenciadores de Tags',
            'webmail': 'Webmail',
            'hosting_panels': 'Painéis de Hospedagem',
            'control_systems': 'Sistemas de Controle',
            'payment_processors': 'Processadores de Pagamento',
            'font_scripts': 'Scripts de Fonte',
            'webcams': 'Webcams',
            'webinar': 'Webinar',
            'database': 'Banco de Dados',
            'network_devices': 'Dispositivos de Rede',
            'remote_access': 'Acesso Remoto',
            'marketing_automation': 'Automação de Marketing',
            'live_chat': 'Chat ao Vivo',
            'builders': 'Construtores',
            'web_hosting': 'Hospedagem Web',
            'dns_server': 'Servidor DNS'
        }
        
        # Agrupa tecnologias por categoria
        tech_by_category = {}
        for tech, info in result['technologies'].items():
            category = info.get('category', 'other')
            if category not in tech_by_category:
                tech_by_category[category] = []
            tech_by_category[category].append((tech, info))
        
        # Mostra tecnologias por categoria
        for category, techs in tech_by_category.items():
            if techs:  # Só mostra categorias que têm tecnologias
                category_name = categories.get(category, category.upper())
                print(f"\n{category_name}:")
                for tech, info in techs:
                    print(f"- {tech}")
                    if info.get('version'):
                        print(f"  Versão: {info['version']}")
                    if info.get('description'):
                        print(f"  Descrição: {info['description']}")
        
        # Mostra informações do servidor
        print("\n=== Informações do Servidor ===")
        for key, value in result['server'].items():
            print(f"- {key}: {value}")
        
        # Mostra meta informações relevantes
        if result['meta']:
            print("\n=== Meta Informações ===")
            for key, value in result['meta'].items():
                if value:  # Só mostra se tiver valor
                    print(f"- {key}: {value}")

if __name__ == "__main__":
    main() 