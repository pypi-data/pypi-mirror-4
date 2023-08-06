# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'Dashboard',
    'name_bg_BG': 'Табло',
    'name_de_DE': 'Dashboard',
    'name_es_CO': 'Escritorio',
    'name_es_ES': 'Escritorio',
    'name_fr_FR': 'Tableau de bord',
    'name_nl_NL': 'Prikbord',
    'name_ru_RU': 'Информационная панель',
    'version': '2.0.1',
    'author': 'B2CK',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': '''Dashboard:
    - Allow to create a personalized dashboard.
''',
    'description_bg_BG': '''Табло:
    - Позволява създаване на перосонализирани табла.
''',
    'description_de_DE': '''Dashboard:
    - Ermöglicht die Einrichtung einer personalisierten Startseite.
''',
    'description_es_CO': '''Escritorio:
    - Permite la creación de una página de inicio personalizada.
''',
    'description_es_ES': '''Escritorio:
    - Permite la creación de una página de inicio personalizada.
''',
    'description_fr_FR': '''Tableau de bord
    - Permet de créer un tableau de bord personalisé.
''',
    'description_nl_NL': '''Prikbord:
    - Maakt een persoonlijk prikbord mogelijk.
''',
    'description_ru_RU': '''Информационная панель:
    - позволяет создавать персональные панели.
''',
    'depends': [
        'ir',
        'res',
    ],
    'xml': [
        'dashboard.xml',
        'res.xml',
        'ir.xml',
    ],
    'translation': [
        'bg_BG.csv',
        'de_DE.csv',
        'es_CO.csv',
        'es_ES.csv',
        'fr_FR.csv',
        'nl_NL.csv',
        'ru_RU.csv',
    ],
}
