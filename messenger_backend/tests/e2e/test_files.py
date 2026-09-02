import pytest
from uuid import uuid4

from src.schemas.enums import ChatType, MessageType
from tests.helpers.assertions import HttpAssertions, FilesAssertions
from tests.helpers import url_builder, FileFactory


class TestFiles:
    """Тесты для работы с файлами"""

    # URLs
    upload_file_url = url_builder.files("messages", "upload_file")
    download_file_url = url_builder.files("messages", "download_file")
    delete_file_url = url_builder.files("messages", "delete_file")

    class TestUploadFile:
        """Тесты загрузки файла"""

        class TestDialog:
            """Тесты для диалогов"""

            @pytest.mark.asyncio
            async def test_upload_file_in_dialog_success(
                self, auth_client_user_1, created_dialog_user1_user3, test_text_file
            ):
                """Тест: успешная загрузка файла в диалог"""
                chat_id = created_dialog_user1_user3.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_success_response(response, dict, 200)
                result = response.json()
                assert "file_url" in result
                assert result["file_url"] is not None

                # Проверяем, что файл сохранен и удаляем его
                FilesAssertions.assert_file_exists_and_delete(
                    file_path=result["file_url"], chat_id=chat_id
                )

            @pytest.mark.asyncio
            async def test_upload_image_in_dialog_success(
                self,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_image_file,
            ):
                """Тест: загрузка изображения в диалог"""
                chat_id = created_dialog_user1_user2.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.IMAGE,
                }

                with open(test_image_file, "rb") as f:
                    files = {"upload_file": ("test.jpg", f, "image/jpeg")}
                    response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_success_response(response, dict, 200)
                result = response.json()
                assert "file_url" in result
                assert result["file_url"] is not None

                # Проверяем, что файл сохранен и удаляем его
                FilesAssertions.assert_file_exists_and_delete(
                    file_path=result["file_url"], chat_id=chat_id
                )

            @pytest.mark.asyncio
            async def test_upload_voice_in_dialog_success(
                self,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_audio_file,
            ):
                """Тест: загрузка аудио в диалог"""
                chat_id = created_dialog_user1_user2.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.VOICE,
                }

                with open(test_audio_file, "rb") as f:
                    files = {"upload_file": ("test.mp3", f, "audio/mpeg")}
                    response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_success_response(response, dict, 200)
                result = response.json()
                assert "file_url" in result
                assert result["file_url"] is not None

                # Проверяем, что файл сохранен и удаляем его
                FilesAssertions.assert_file_exists_and_delete(
                    file_path=result["file_url"], chat_id=chat_id
                )

            @pytest.mark.asyncio
            async def test_upload_file_in_dialog_not_member(
                self,
                auth_client_user_2,
                created_dialog_user1_user3,
                test_text_file,
            ):
                """Тест: загрузка файла в диалог, где пользователь не участник"""
                chat_id = created_dialog_user1_user3.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_2.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Вы не являетесь участником данного диалога",
                    expected_status=403,
                )

        class TestGroup:
            """Тесты для групп"""

            @pytest.mark.asyncio
            async def test_upload_file_in_group_success(
                self,
                auth_client_user_1,
                created_group_user1_user2_user3,
                test_text_file,
            ):
                """Тест: успешная загрузка текстового файла в группу"""
                chat_id = created_group_user1_user2_user3.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_success_response(response, dict, 200)
                result = response.json()
                assert result["file_url"] is not None

                # Проверяем, что файл сохранен и удаляем его
                FilesAssertions.assert_file_exists_and_delete(
                    file_path=result["file_url"], chat_id=chat_id
                )

            @pytest.mark.asyncio
            async def test_upload_file_in_group_not_member(
                self,
                auth_client_user_2,
                created_group_user1_user3,
                test_text_file,
            ):
                """Тест: загрузка файла в группу, где пользователь не участник"""
                chat_id = created_group_user1_user3.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_2.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Вы не являетесь участником группы",
                    expected_status=403,
                )

        class TestCommon:
            """Общие тесты для всех чатов"""

            @pytest.mark.asyncio
            async def test_upload_file_wrong_chat_type(
                self,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_text_file,
            ):
                """Тест: загрузка файла с неверным типом чата"""
                chat_id = created_dialog_user1_user2.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_not_found_error(
                    response=response,
                    expected_message="Группа не найдена",
                )

            @pytest.mark.asyncio
            async def test_upload_file_wrong_file_type_for_message(
                self,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_text_file,
            ):
                """Тест: загрузка файла с типом IMAGE, но с txt файлом"""
                chat_id = created_dialog_user1_user2.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.IMAGE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Для типа сообщения image, не подходит тип файла text/plain",
                    expected_status=415,
                )

            @pytest.mark.asyncio
            async def test_upload_file_unauthorized(
                self,
                client,
                created_dialog_user1_user2,
                test_text_file,
            ):
                """Тест: загрузка файла без авторизации"""
                chat_id = created_dialog_user1_user2.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    response = await client.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
                )

            @pytest.mark.asyncio
            async def test_upload_file_invalid_token(
                self,
                client,
                created_dialog_user1_user2,
                test_text_file,
            ):
                """Тест: загрузка файла с невалидным токеном"""
                client.headers["Authorization"] = "Bearer invalid_token"
                chat_id = created_dialog_user1_user2.id

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    response = await client.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Невалидный токен",
                )

            @pytest.mark.asyncio
            async def test_upload_file_non_existent_chat(
                self,
                auth_client_user_1,
                test_text_file,
            ):
                """Тест: загрузка файла в несуществующий чат"""
                chat_id = uuid4()

                data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_not_found_error(
                    response=response,
                    expected_message="Диалог не найден",
                )

    class TestDownloadFile:
        """Тесты скачивания файла"""

        class TestDialog:
            """Тесты для диалогов"""

            @pytest.mark.asyncio
            async def test_download_in_dialog_success(
                self,
                auth_client_user_1,
                created_dialog_user1_user3,
                test_text_file,
            ):
                """Тест: успешное скачивание файла из диалога"""
                # загружаем файл
                chat_id = created_dialog_user1_user3.id
                upload_data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    upload_response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=upload_data,
                        files=files,
                    )

                upload_result = upload_response.json()
                file_url = upload_result["file_url"]

                # Скачиваем файл
                download_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                }

                response = await auth_client_user_1.post(
                    TestFiles.download_file_url,
                    json=download_data,
                )

                assert response.status_code == 200
                assert "Content-Disposition" in response.headers
                assert (
                    response.headers["Content-Disposition"]
                    == 'attachment; filename="test.txt"'
                )
                assert "text/plain" in response.headers["content-type"]
                assert response.content == b"Test file content for message"

                FilesAssertions.assert_file_exists_and_delete(
                    file_path=file_url, chat_id=chat_id
                )

            @pytest.mark.asyncio
            async def test_download_file_not_dialog_member(
                self,
                auth_client_user_1,
                created_dialog_user1_user3,
                auth_client_user_2,
                test_text_file,
            ):
                """Тест: скачивание файла не участником диалога"""
                # Загружаем файл от user_1
                chat_id = created_dialog_user1_user3.id
                upload_data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    upload_response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=upload_data,
                        files=files,
                    )

                upload_result = upload_response.json()
                file_url = upload_result["file_url"]

                # Пытается скачать user_2 (не участник)
                download_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                }

                response = await auth_client_user_2.post(
                    TestFiles.download_file_url,
                    json=download_data,
                )

                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Вы не являетесь участником данного диалога",
                    expected_status=403,
                )

                # Очищаем
                FilesAssertions.assert_file_exists_and_delete(
                    file_path=file_url, chat_id=chat_id
                )

        class TestGroup:
            """Тесты для групп"""

            @pytest.mark.asyncio
            async def test_download_in_group_success(
                self,
                auth_client_user_1,
                created_group_user1_user2_user3,
                test_text_file,
            ):
                """Тест: успешное скачивание файла из диалога"""
                # загружаем файл
                chat_id = created_group_user1_user2_user3.id
                upload_data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    upload_response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=upload_data,
                        files=files,
                    )

                upload_result = upload_response.json()
                file_url = upload_result["file_url"]

                # Скачиваем файл
                download_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                }

                response = await auth_client_user_1.post(
                    TestFiles.download_file_url,
                    json=download_data,
                )

                assert response.status_code == 200
                assert "Content-Disposition" in response.headers
                assert (
                    response.headers["Content-Disposition"]
                    == 'attachment; filename="test.txt"'
                )
                assert "text/plain" in response.headers["content-type"]
                assert response.content == b"Test file content for message"

                FilesAssertions.assert_file_exists_and_delete(
                    file_path=file_url, chat_id=chat_id
                )

            @pytest.mark.asyncio
            async def test_download_file_not_group_member(
                self,
                auth_client_user_1,
                auth_client_user_2,
                created_group_user1_user3,
                test_text_file,
            ):
                """Тест: скачивание файла не участником группы"""
                # Загружаем файл от user_1
                chat_id = created_group_user1_user3.id
                upload_data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    upload_response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=upload_data,
                        files=files,
                    )
                upload_result = upload_response.json()
                file_url = upload_result["file_url"]

                # Пытается скачать user_2 (не участник)
                download_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                }

                response = await auth_client_user_2.post(
                    TestFiles.download_file_url,
                    json=download_data,
                )

                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Вы не являетесь участником группы",
                    expected_status=403,
                )
                # Очищаем
                FilesAssertions.assert_file_exists_and_delete(file_url, chat_id)

        class TestCommon:
            """Общие тесты для всех чатов"""

            @pytest.mark.asyncio
            async def test_download_non_existent_file(
                self,
                auth_client_user_1,
                created_dialog_user1_user2,
            ):
                """Тест: скачивание несуществующего файла"""
                chat_id = created_dialog_user1_user2.id
                file_url = f"chats/{chat_id}/file/non_existent.txt"

                download_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                }

                response = await auth_client_user_1.post(
                    TestFiles.download_file_url,
                    json=download_data,
                )

                HttpAssertions.assert_not_found_error(
                    response=response,
                    expected_message="Файл не найден",
                )

            @pytest.mark.asyncio
            async def test_download_file_unauthorized(
                self,
                client,
                created_dialog_user1_user2,
            ):
                """Тест: скачивание файла без авторизации"""
                chat_id = created_dialog_user1_user2.id
                download_data = {
                    "file_path": "chats/file.txt",
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                }

                response = await client.post(
                    TestFiles.download_file_url,
                    json=download_data,
                )

                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
                )

            @pytest.mark.asyncio
            async def test_download_file_invalid_token(
                self,
                client,
                created_dialog_user1_user2,
            ):
                """Тест: скачивание файла с невалидным токеном"""
                client.headers["Authorization"] = "Bearer invalid_token"
                chat_id = created_dialog_user1_user2.id

                download_data = {
                    "file_path": "chats/file.txt",
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                }
                response = await client.post(
                    TestFiles.download_file_url,
                    json=download_data,
                )
                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Невалидный токен",
                )

            @pytest.mark.asyncio
            async def test_download_file_non_existent_chat(self, auth_client_user_1):
                """Тест: скачивание файла из несуществующего чата"""
                chat_id = uuid4()

                download_data = {
                    "file_path": "chats/file.txt",
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                }
                response = await auth_client_user_1.post(
                    TestFiles.download_file_url,
                    json=download_data,
                )
                HttpAssertions.assert_not_found_error(
                    response=response,
                    expected_message="Диалог не найден",
                )

    class TestDeleteFile:
        """Тесты удаления файла"""

        class TestDialog:
            """Тесты для диалогов"""

            @pytest.mark.asyncio
            async def test_delete_file_in_dialog_success(
                self,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_text_file,
            ):
                """Тест: успешное удаление файла из диалога"""
                # загружаем файл
                chat_id = created_dialog_user1_user2.id
                upload_data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    upload_response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=upload_data,
                        files=files,
                    )

                upload_result = upload_response.json()
                file_url = upload_result["file_url"]

                # Проверяем, что файл существует
                FilesAssertions.assert_file_exists(file_url)

                # удаляем файл
                delete_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                }

                response = await auth_client_user_1.request(
                    url=TestFiles.delete_file_url,
                    method="DELETE",
                    json=delete_data,
                )

                HttpAssertions.assert_success_response(response, dict, 200)
                result = response.json()
                assert result["deleted"] is True

                # Проверяем, что файл удален
                FilesAssertions.assert_file_not_exists(file_url)
                FileFactory.cleanup_test_messages_files(chat_id)

            @pytest.mark.asyncio
            async def test_delete_file_not_dialog_member(
                self,
                auth_client_user_1,
                auth_client_user_2,
                created_dialog_user1_user3,
                test_text_file,
            ):
                """Тест: удаление файла не участником диалога"""
                # загружаем файл от user_1
                chat_id = created_dialog_user1_user3.id
                upload_data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    upload_response = await auth_client_user_1.post(
                        url=TestFiles.upload_file_url,
                        data=upload_data,
                        files=files,
                    )

                upload_result = upload_response.json()
                file_url = upload_result["file_url"]

                # пытается удалить user_2 (не участник)
                delete_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS.value,
                }

                response = await auth_client_user_2.request(
                    url=TestFiles.delete_file_url,
                    method="DELETE",
                    json=delete_data,
                )

                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Вы не являетесь участником данного диалога",
                    expected_status=403,
                )
                # Очищаем
                FilesAssertions.assert_file_exists_and_delete(file_url, chat_id)

        class TestGroup:
            """Тесты для групп"""

            @pytest.mark.asyncio
            async def test_delete_file_in_group_success(
                self,
                auth_client_user_1,
                created_group_user1_user2_user3,
                test_text_file,
            ):
                """Тест: успешное удаление файла из группы"""
                # загружаем файл
                chat_id = created_group_user1_user2_user3.id
                upload_data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    upload_response = await auth_client_user_1.post(
                        TestFiles.upload_file_url,
                        data=upload_data,
                        files=files,
                    )

                upload_result = upload_response.json()
                file_url = upload_result["file_url"]

                # Проверяем, что файл существует
                FilesAssertions.assert_file_exists(file_url)

                # удаляем файл
                delete_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                }

                response = await auth_client_user_1.request(
                    url=TestFiles.delete_file_url,
                    method="DELETE",
                    json=delete_data,
                )

                HttpAssertions.assert_success_response(response, dict, 200)
                result = response.json()
                assert result["deleted"] is True

                # Проверяем, что файл удален
                FilesAssertions.assert_file_not_exists(file_url)
                FileFactory.cleanup_test_messages_files(chat_id)

            @pytest.mark.asyncio
            async def test_delete_file_not_group_member(
                self,
                auth_client_user_1,
                auth_client_user_2,
                created_group_user1_user3,
                test_text_file,
            ):
                """Тест: удаление файла не участником группы"""
                # загружаем файл от user_1
                chat_id = created_group_user1_user3.id
                upload_data = {
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                    "file_type": MessageType.FILE,
                }

                with open(test_text_file, "rb") as f:
                    files = {"upload_file": ("test.txt", f, "text/plain")}
                    upload_response = await auth_client_user_1.post(
                        url=TestFiles.upload_file_url,
                        data=upload_data,
                        files=files,
                    )

                upload_result = upload_response.json()
                file_url = upload_result["file_url"]

                # пытается удалить user_2 (не участник)
                delete_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.GROUP,
                }

                response = await auth_client_user_2.request(
                    url=TestFiles.delete_file_url,
                    method="DELETE",
                    json=delete_data,
                )

                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Вы не являетесь участником группы",
                    expected_status=403,
                )
                # Очищаем
                FilesAssertions.assert_file_exists_and_delete(file_url, chat_id)

        class TestCommon:
            """Общие тесты для всех чатов"""

            @pytest.mark.asyncio
            async def test_delete_non_existent_file(
                self,
                auth_client_user_1,
                created_dialog_user1_user2,
            ):
                """
                Тест: удаление несуществующего файла
                Ожидается: deleted=False
                """
                chat_id = created_dialog_user1_user2.id
                file_url = f"chats/{chat_id}/file/non_existent.txt"

                delete_data = {
                    "file_path": file_url,
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                }

                response = await auth_client_user_1.request(
                    url=TestFiles.delete_file_url,
                    method="DELETE",
                    json=delete_data,
                )

                HttpAssertions.assert_success_response(response, dict, 200)
                result = response.json()
                assert result["deleted"] is False

            @pytest.mark.asyncio
            async def test_delete_file_unauthorized(
                self,
                client,
                created_dialog_user1_user2,
            ):
                """Тест: удаление файла без авторизации"""
                chat_id = created_dialog_user1_user2.id
                delete_data = {
                    "file_path": "chats/file.txt",
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS,
                }

                response = await client.request(
                    url=TestFiles.delete_file_url,
                    method="DELETE",
                    json=delete_data,
                )

                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
                )

            @pytest.mark.asyncio
            async def test_delete_file_invalid_token(
                self,
                client,
                created_dialog_user1_user2,
            ):
                """Тест: удаление файла с невалидным токеном"""
                client.headers["Authorization"] = "Bearer invalid_token"
                chat_id = created_dialog_user1_user2.id
                delete_data = {
                    "file_path": "chats/file.txt",
                    "chat_id": str(chat_id),
                    "chat_type": ChatType.DIALOGS.value,
                }

                response = await client.request(
                    url=TestFiles.delete_file_url,
                    method="DELETE",
                    json=delete_data,
                )

                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Невалидный токен",
                )
