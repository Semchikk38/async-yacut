# conftest.py
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from contextlib import suppress
from hashlib import md5
from urllib.parse import quote, unquote

from tests.yandex_disk_mock_server import (
    COMMON_ASSERT_MSG_FOR_UPLOAD_FILES,
    REQUEST_UPLOAD_URL,
    UPLOAD_URL,
    DOWNLOAD_LINK_URL,
)


def _check_headers(path, headers):
    assert 'Authorization' in headers, (
        f'Убедитесь, что в запросе к `{path}` '
        'передаётся заголовок Authorization.'
    )


async def _handle_fields_param(request, response_data):
    fields = request.query.get('fields')
    if fields:
        to_remove = response_data.keys() - set(fields.split(','))
        for k in to_remove:
            del response_data[k]
    return response_data


def _make_get_upload_link_handler(user_calls, file_names):
    async def handler(request):
        user_calls.add('get_upload_link')
        _check_headers(request.path, request.headers)
        assert 'path' in request.query, 'Отсутствует параметр path'
        path_param = request.query['path']
        with suppress(Exception):
            path_param = unquote(path_param)
        assert '/' in path_param, 'path не содержит /'
        file_name = path_param.split('/')[-1]
        path_hash = md5(request.query['path'].encode()).hexdigest()
        file_names[path_hash] = file_name
        link = f'http://{request.host}{UPLOAD_URL}/{path_hash}'
        response_data = await _handle_fields_param(request, {
            'href': link, 'method': 'PUT', 'templated': False
        })
        return web.json_response(response_data, status=200)
    return handler


def _make_mock_upload_handler(user_calls, file_names):
    async def handler(request):
        user_calls.add('upload')
        request_data = await request.read()
        assert request_data, 'Данные файла отсутствуют'
        location_header = '/disk/' + quote(file_names[request.url.name])
        return web.Response(headers={'Location': location_header}, status=201)
    return handler


def _make_mock_get_download_link_handler(user_calls):
    async def handler(request):
        user_calls.add('get_download_link')
        _check_headers(request.path, request.headers)
        assert 'path' in request.query
        path_hash = md5(request.query['path'].encode()).hexdigest()
        link = f'http://{request.host}/disk/{path_hash}'
        response_data = await _handle_fields_param(request, {
            'href': link, 'method': 'GET', 'templated': False
        })
        return web.json_response(response_data, status=200)
    return handler


async def _mock_publish_handler(request):
    return web.json_response({}, status=200)


async def _disk_info_handler(request):
    return web.json_response({
        'is_paid': True, 'max_file_size': 53687091200,
        'paid_max_file_size': 53687091200,
        'reg_time': '2016-08-28T08:00:34+00:00', 'revision': 1718044099614274,
        'system_folders': {'applications': 'disk:/Приложения'},
        'total_space': 2478196129792, 'trash_size': 1574013,
        'unlimited_autoupload_enabled': False, 'used_space': 20888456034
    }, status=200)


async def _resource_handler(request):
    public_url = f'http://{request.host}/public/{quote(request.query["path"])}'
    return web.json_response({'public_url': public_url})


async def _catch_all_handler(request):
    raise AssertionError(COMMON_ASSERT_MSG_FOR_UPLOAD_FILES)


@pytest.fixture
def mock_server(event_loop):
    async def _setup():
        user_calls = set()
        file_names = {}

        app = web.Application()
        app.router.add_get(
            REQUEST_UPLOAD_URL, _make_get_upload_link_handler(
                user_calls, file_names))
        app.router.add_put(
            UPLOAD_URL + '/{path_hash}', _make_mock_upload_handler(
                user_calls, file_names))
        app.router.add_get(
            DOWNLOAD_LINK_URL, _make_mock_get_download_link_handler(
                user_calls))
        app.router.add_put('/v1/disk/resources/publish', _mock_publish_handler)
        app.router.add_get('/v1/disk/', _disk_info_handler)
        app.router.add_get('/v1/disk/resources', _resource_handler)
        app.router.add_route('*', '/{tail:.*}', _catch_all_handler)

        server = TestServer(app, loop=event_loop)
        await server.start_server()
        return server, user_calls

    return _setup()