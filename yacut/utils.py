# yacut/utils.py
import asyncio
import aiohttp
from urllib.parse import unquote
import string
import secrets

from .models import URLMap
from .constants import SHORT_ID_REGEX

CHARS = string.ascii_letters + string.digits
DISK_API_HOST = 'https://cloud-api.yandex.net'
DISK_API_VERSION = 'v1'
REQUEST_UPLOAD_URL = (
    f'{DISK_API_HOST}/{DISK_API_VERSION}/disk/resources/upload'
)
DOWNLOAD_LINK_URL = (
    f'{DISK_API_HOST}/{DISK_API_VERSION}/disk/resources/download'
)
PUBLISH_URL = (
    f'{DISK_API_HOST}/{DISK_API_VERSION}/disk/resources/publish'
)


async def _upload_single_file(session, token, file_storage, filename):
    headers = {'Authorization': f'OAuth {token}'}

    params = {'path': f'app:/{filename}', 'overwrite': 'true'}
    async with session.get(REQUEST_UPLOAD_URL, headers=headers,
                           params=params) as resp:
        resp.raise_for_status()
        upload_data = await resp.json()
        upload_url = upload_data['href']
        method = upload_data.get('method', 'PUT')

    file_data = file_storage.read()
    async with session.request(method, upload_url, data=file_data) as resp:
        resp.raise_for_status()
        location = resp.headers.get('Location', '')
        if not location:
            raise RuntimeError(
                'Не удалось получить расположение файла на Диске')
        file_path = unquote(location).replace('/disk', '')

    async with session.get(DOWNLOAD_LINK_URL, headers=headers,
                           params={'path': file_path}) as resp:
        resp.raise_for_status()
        _ = await resp.json()

    async with session.put(PUBLISH_URL, headers=headers,
                           params={'path': file_path}) as resp:
        resp.raise_for_status()
    async with session.get(
        f'{DISK_API_HOST}/{DISK_API_VERSION}/disk/resources',
        headers=headers,
        params={'path': file_path, 'fields': 'public_url'}
    ) as resp:
        resp.raise_for_status()
        meta = await resp.json()
        public_url = meta['public_url']

    return filename, public_url


async def _upload_files(files_list, token):
    async with aiohttp.ClientSession() as session:
        tasks = [
            _upload_single_file(session, token, file_storage, filename)
            for file_storage, filename in files_list
        ]
        return await asyncio.gather(*tasks)


def upload_files_to_disk(files_list, token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_upload_files(files_list, token))
    finally:
        loop.close()


def get_unique_short_id(length=6):
    while True:
        short = ''.join(secrets.choice(CHARS) for _ in range(length))
        if not URLMap.get_by_short(short):
            return short


def is_valid_short_id(short):
    return bool(SHORT_ID_REGEX.match(short))