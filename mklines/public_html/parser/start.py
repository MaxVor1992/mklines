# -*- coding: utf-8 -*-
import sys, os
sys.path.append('/home/r/rapcooc5/mklines/public_html/parser/parser_app') # указываем директорию с проектом
sys.path.append('c:\\Users\\karim\\Coding\\parser\\venv38_flask\\lib\\python3.8\\site-packages') # указываем директорию с проектом
sys.path.append('/home/r/rapcooc5/mklines/public_html/parser/venv38_flask/lib/python3.8/site-packages') # указываем директорию с библиотеками, куда поставили Flask
#from parser_app import app as application # когда Flask стартует, он ищет application. Если не указать 'as application', сайт не заработает
import parser_app
application = parser_app.create_app()
from werkzeug.debug import DebuggedApplication # Опционально: подключение модуля отладки
application.wsgi_app = DebuggedApplication(application.wsgi_app, True) # Опционально: включение модуля отадки
application.debug = True  # Опционально: True/False устанавливается по необходимости в отладке
application.run(debug=True)
