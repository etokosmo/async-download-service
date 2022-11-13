import asyncio
import os

import aiofiles
from aiohttp import web

CHUNK_SIZE = 100


async def archive(request):
    archive_hash = request.match_info.get('archive_hash')
    archive_path = os.path.join('test_photos', archive_hash)
    # TODO import 'test_photos' from env or as argument

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'attachment; \
        filename="filename.zip"'
    # TODO import filename from env or as argument
    process = await asyncio.create_subprocess_exec(
        'zip', '-r', '-', '.',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=archive_path)

    await response.prepare(request)

    while not process.stdout.at_eof():
        # convert chunk from kilobytes to bytes
        chunk = await process.stdout.read(CHUNK_SIZE * 1024)
        await response.write(chunk)
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
