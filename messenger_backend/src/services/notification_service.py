from src.schemas import MessageResponse


class NotificationService:
    """Сервис для отправки push-уведомлений"""

    @staticmethod
    async def send_push_notifications(
        usernames: list[str],
        message: MessageResponse
    ):
        """ Отправка push-уведомлений офлайн-пользователям """
        # TODO: Отдельные классы уведомлений для Firebase, локалки и т.д (notofication_manager)
        for username in usernames:
            print(f"🦎 Уведомление для {username}: Сообщение от {message.sender.username}{"\n"}({message.content})")