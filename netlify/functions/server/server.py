# Netlify Serverless Function для Flask приложения
# Этот файл нужен для деплоя на Netlify через serverless functions

import sys
import os

# Добавляем путь к корню проекта (на 3 уровня выше от netlify/functions/server/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from serverless_wsgi import handle_request
    from app import app
    
    def handler(event, context):
        """Handler для Netlify Functions через serverless-wsgi"""
        return handle_request(app, event, context)
except ImportError:
    # Fallback если serverless-wsgi не установлен
    from app import app
    
    def handler(event, context):
        """Handler для Netlify Functions (fallback)"""
        # Простая обработка запросов без serverless-wsgi
        # Рекомендуется установить serverless-wsgi
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': 'Please install serverless-wsgi: pip install serverless-wsgi'
        }

