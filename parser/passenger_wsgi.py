# -*- coding: utf-8 -*-
import sys, os

# Добавляем пути к проекту и виртуальному окружению
sys.path.append('/home/r/rapcooc5/mklines/public_html/parser/parser_app')
sys.path.append('/home/r/rapcooc5/mklines/public_html/parser/venv38_flask/lib/python3.8/site-packages')

# Импортируем приложение
from parser_app import create_app

application = create_app()

# Отладка только в development режиме
if os.environ.get('FLASK_ENV') == 'development':
    from werkzeug.debug import DebuggedApplication
    application.wsgi_app = DebuggedApplication(application.wsgi_app, True)
    application.debug = True
else:
    application.debug = False
