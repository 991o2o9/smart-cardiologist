#!/usr/bin/env python3
"""
Тест для проверки работы fastapi-babel
"""

from fastapi_babel import Babel, BabelConfigs
import pathlib

def test_babel():
    try:
        # Создаем конфигурацию для Babel
        configs = BabelConfigs(
            ROOT_DIR=pathlib.Path(__file__).parent,
            BABEL_DEFAULT_LOCALE="en",
            BABEL_TRANSLATION_DIRECTORY="locale",
            BABEL_DOMAIN="messages"
        )
        
        print(f"Configs created: {configs}")
        print(f"ROOT_DIR: {configs.ROOT_DIR}")
        print(f"BABEL_DEFAULT_LOCALE: {configs.BABEL_DEFAULT_LOCALE}")
        print(f"BABEL_TRANSLATION_DIRECTORY: {configs.BABEL_TRANSLATION_DIRECTORY}")
        print(f"BABEL_DOMAIN: {configs.BABEL_DOMAIN}")
        
        # Создаем экземпляр Babel
        babel = Babel(configs)
        print("Babel instance created successfully")
        
        # Устанавливаем английскую локаль
        babel.locale = "en"
        print(f"Current locale: {babel.locale}")
        
        # Пытаемся получить перевод
        try:
            result = babel.gettext("greeting")
            print(f"English translation: {result}")
        except Exception as e:
            print(f"Error getting English translation: {e}")
        
        # Устанавливаем русскую локаль
        babel.locale = "ru"
        print(f"Current locale: {babel.locale}")
        
        try:
            result = babel.gettext("greeting")
            print(f"Russian translation: {result}")
        except Exception as e:
            print(f"Error getting Russian translation: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_babel()
