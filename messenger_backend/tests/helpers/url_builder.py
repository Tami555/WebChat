class URLBuilder:
    """Построитель URL для тестов"""

    API_V1 = "/api/v1"

    def __init__(self, base_path: str = API_V1):
        self.base_path = base_path

    def build(self, *parts: str) -> str:
        """Собирает URL из частей"""
        parts = [p.strip("/") for p in parts if p]
        return f"{self.base_path}/" + "/".join(parts)

    # готовые методы для групп эндпоинтов
    def auth(self, *parts: str) -> str:
        return self.build("auth", *parts)

    def chats(self, *parts: str) -> str:
        return self.build("chats", *parts)

    def files(self, *parts: str) -> str:
        return self.build("files", *parts)

    def users(self, *parts: str) -> str:
        return self.build("users", *parts)

    def dialogs(self, *parts: str) -> str:
        return self.build("dialogs", *parts)


url_builder = URLBuilder()


def build_url(*parts: str) -> str:
    """Собрать URL вручную"""
    return URLBuilder().build(*parts)
