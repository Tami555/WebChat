import random


class VerificationCodeGenerator:
    """Генератор кодов верификации"""
    
    @staticmethod
    def generate_from_phone(phone: str, length: int = 6) -> str:
        """ Генерация липового кода из последних цифр телефона """
        digits = ''.join(filter(str.isdigit, phone))
        code = digits[-length:]
        return code
    
    @staticmethod
    def generate_random(length: int = 6) -> str:
        """Генерация случайного кода"""
        return ''.join(str(random.randint(0, 9)) for _ in range(length))