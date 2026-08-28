from typing import Dict, Any


class StickerDataFactory:
    """Фабрика данных для стикеров"""

    @staticmethod
    def sticker_data(
        name: str = "Test Sticker",
        emoji: str = "⭐",
        file_url: str = "/test/sticker.png",
    ) -> Dict[str, Any]:
        """Данные для создания стикера"""
        return {
            "name": name,
            "emoji": emoji,
            "file_url": file_url,
        }

    @staticmethod
    def sticker_pack_data(
        name: str = "Test Pack",
        is_premium: bool = False,
    ) -> Dict[str, Any]:
        """Данные для создания стикерпака"""
        return {
            "name": name,
            "is_premium": is_premium,
        }

    @staticmethod
    def create_sticker_custom(**kwargs) -> Dict[str, Any]:
        """Создание кастомного стикера"""
        defaults = StickerDataFactory.sticker_data()
        defaults.update(kwargs)
        return defaults

    @staticmethod
    def create_sticker_pack_custom(**kwargs) -> Dict[str, Any]:
        """Создание кастомного стикерПака"""
        defaults = StickerDataFactory.sticker_pack_data()
        defaults.update(kwargs)
        return defaults
