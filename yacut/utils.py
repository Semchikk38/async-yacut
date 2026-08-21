import asyncio
from urllib.parse import unquote

import aiohttp

from .config import Config

AUTH_HEADERS = {'Authorization': f'OAuth {Config.DISK_TOKEN}'}
RESOURCE_URL = (
    f'{Config.DISK_API_HOST}/{Config.DISK_API_VERSION}/disk/resources'
)


async def _upload_single_file(session, file_storage, filename):
    headers = AUTH_HEADERS
    params = {'path': f'app:/{filename}', 'overwrite': 'true'}
    async with session.get(Config.REQUEST_UPLOAD_URL,
                           headers=headers,
                           params=params) as resp:
        resp.raise_for_status()
        upload_data = await resp.json()
        upload_url = upload_data['href']
        method = upload_data.get('method', 'PUT')

    async with session.request(method, upload_url,
                               data=file_storage.read()) as resp:
        resp.raise_for_status()
        file_path = unquote(resp.headers['Location']).replace('/disk', '')

    async with session.get(Config.DOWNLOAD_LINK_URL,
                           headers=headers,
                           params={'path': file_path}) as resp:
        resp.raise_for_status()

    async with session.put(Config.PUBLISH_URL,
                           headers=headers,
                           params={'path': file_path}) as resp:
        resp.raise_for_status()
    async with session.get(RESOURCE_URL,
                           headers=headers,
                           params={'path': file_path,
                                   'fields': 'public_url'}) as resp:
        resp.raise_for_status()
        return (await resp.json())['public_url']


async def _upload_files(files_list):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[_upload_single_file(session, file_storage, filename)
              for file_storage, filename in files_list]
        )


def upload_files_to_disk(files_list):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_upload_files(files_list))
    finally:
        loop.close()
