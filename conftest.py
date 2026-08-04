import pytest
from aiohttp.test_utils import TestServer
from tests.yandex_disk_mock_server import (
    COMMON_ASSERT_MSG_FOR_UPLOAD_FILES,
    REQUEST_UPLOAD_URL,
    UPLOAD_URL,
    DOWNLOAD_LINK_URL,
)

from aiohttp import web
from contextlib import suppress
from hashlib import md5
from urllib.parse import quote, unquote

@pytest.fixture
def mock_server(event_loop):
    """Синхронная фикстура, возвращающая корутину для настройки мок-сервера."""
    async def _setup():
        user_calls = set()
        file_names = {}

        async def check_headers(path, headers):
            assert 'Authorization' in headers, (
                'Убедитесь, что в запросе к эндпоинту Яндекс Диска '
                f'`{path}` передаётся заголовок `Authorization` с токеном доступа.'
            )

        async def handle_fields_param(request, response_data):
            fields_query_param = request.query.get('fields')
            if fields_query_param:
                keys_to_remove = (
                    response_data.keys() - set(fields_query_param.split(','))
                )
                for key in keys_to_remove:
                    del response_data[key]
            return response_data

        async def get_upload_link_handler(request):
            user_calls.add('get_upload_link')
            await check_headers(request.path, request.headers)
            assert 'path' in request.query
            path_param = request.query['path']
            with suppress(Exception):
                path_param = unquote(path_param)
            assert '/' in path_param
            file_name = path_param.split('/')[-1]
            path_hash = md5(request.query['path'].encode()).hexdigest()
            file_names[path_hash] = file_name

            link = f'http://{request.host}{UPLOAD_URL}/{path_hash}'
            response_data = await handle_fields_param(
                request,
                {
                    'href': link,
                    'method': 'PUT',
                    'templated': False
                }
            )
            return web.json_response(response_data, status=200)

        async def mock_upload_handler(request):
            user_calls.add('upload')
            request_data = await request.read()
            assert request_data, (
                'Убедитесь, что PUT-запрос на загрузку файла на Яндекс Диск '
                'содержит загружаемые данные.'
            )
            location_header = '/disk/{}'.format(
                quote(file_names[request.url.name])
            )
            return web.Response(headers={'Location': location_header}, status=201)

        async def mock_get_download_link_handler(request):
            user_calls.add('get_download_link')
            await check_headers(request.path, request.headers)
            assert 'path' in request.query
            path_hash = md5(request.query['path'].encode()).hexdigest()
            link = f'http://{request.host}/disk/{path_hash}'
            response_data = await handle_fields_param(
                request,
                {
                    'href': link,
                    'method': 'GET',
                    'templated': False
                }
            )
            return web.json_response(response_data, status=200)

        async def mock_publish_handler(request):
            # Эндпоинт публикации: ничего не добавляем в user_calls,
            # чтобы тест не проверял его наличие (но можем добавить при желании)
            # Возвращаем успех, дальше ресурс вернёт public_url
            return web.json_response({}, status=200)

        async def disk_info_handler(request):
            return web.json_response(
                {
                    'is_paid': True,
                    'max_file_size': 53687091200,
                    'paid_max_file_size': 53687091200,
                    'reg_time': '2016-08-28T08:00:34+00:00',
                    'revision': 1718044099614274,
                    'system_folders': {'applications': 'disk:/Приложения'},
                    'total_space': 2478196129792,
                    'trash_size': 1574013,
                    'unlimited_autoupload_enabled': False,
                    'used_space': 20888456034
                },
                status=200
            )

        async def catch_all_handler(request):
            raise AssertionError(COMMON_ASSERT_MSG_FOR_UPLOAD_FILES)

        app = web.Application()
        app.router.add_get(REQUEST_UPLOAD_URL, get_upload_link_handler)
        app.router.add_put(UPLOAD_URL + '/{path_hash}', mock_upload_handler)
        app.router.add_get(DOWNLOAD_LINK_URL, mock_get_download_link_handler)
        app.router.add_put('/v1/disk/resources/publish', mock_publish_handler)  # новый обработчик
        app.router.add_get('/v1/disk/', disk_info_handler)
        # Ресурс для получения метаданных (возвращает публичную ссылку)
        async def resource_handler(request):
            path = request.query['path']
            public_url = f'http://{request.host}/public/{quote(path)}'
            return web.json_response({'public_url': public_url})
        app.router.add_get('/v1/disk/resources', resource_handler)
        app.router.add_route('*', '/{tail:.*}', catch_all_handler)

        server = TestServer(app, loop=event_loop)
        await server.start_server()
        return server, user_calls

    return _setup()
