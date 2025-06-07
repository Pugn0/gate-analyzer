# Web Analyzer Bot

Bot do Telegram para análise completa de tecnologias web em sites.

## Funcionalidades

- Analisa sites em busca de tecnologias web
- Suporta múltiplas URLs simultaneamente
- Formatação bonita dos resultados com emojis
- Detecção de várias categorias de tecnologias:
  - Frameworks (React, Angular, Vue.js, etc.)
  - CMS (WordPress, Drupal, Joomla, etc.)
  - Servidores (Nginx, Apache, etc.)
  - Gateways de pagamento (PayPal, Stripe, etc.)
  - Analytics (Google Analytics, Matomo, etc.)
  - CDN (Cloudflare, Akamai, etc.)
  - E muito mais...

## Como Usar

1. Inicie uma conversa com o bot: [@pugno_analyzer_bot](https://t.me/pugno_analyzer_bot)

2. Use o comando `/start` para ver as instruções iniciais

3. Use o comando `/analyze` seguido das URLs que deseja analisar:
```
/analyze https://site1.com https://site2.com
```

4. O bot irá analisar os sites e retornar todas as tecnologias encontradas, agrupadas por categoria.

## Requisitos

- Python 3.7+
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/wappalazer.git
cd wappalazer
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o token do bot em `config.py`

4. Execute o bot:
```bash
python bot_gateway_analyzer.py
```

## Estrutura do Projeto

- `bot_gateway_analyzer.py`: Script principal do bot
- `config.py`: Configurações do bot
- `technologies.json`: Banco de dados de tecnologias
- `requirements.txt`: Dependências do projeto

## Contribuindo

Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 