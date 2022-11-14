import asyncio
import logging
import os
from functools import partial

import aiofiles
from aiohttp import web
from environs import Env

CHUNK_SIZE = 100  # in kilobytes

logger = logging.getLogger(__name__)


async def archive(request, base_archive_path, process_delay):
    archive_hash = request.match_info.get('archive_hash')
    archive_path = os.path.join(base_archive_path, archive_hash)
    if not os.path.exists(archive_path):
        raise web.HTTPNotFound(text='Архив не существует или был удален')

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

    try:
        chunk_counter = 1
        while not process.stdout.at_eof():
            # read data in chunk converted from kilobytes to bytes
            chunk = await process.stdout.read(CHUNK_SIZE * 1024)
            if process_delay:
                await asyncio.sleep(process_delay)
            logging.info(
                f'{chunk_counter * CHUNK_SIZE}Kb: Sending archive chunk ...')
            await response.write(chunk)
            chunk_counter += 1

    except asyncio.CancelledError:
        logger.error('Download was interrupted')
        raise
    finally:
        if process.returncode:
            process.kill()
            await process.communicate()
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    env = Env()
    env.read_env()
    base_archive_path = env('BASE_ARCHIVE_PATH', 'test_photos')
    activate_logs = env.bool('ACTIVATE_LOGS', True)
    process_delay = env.int('PROCESS_DELAY', 0)

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s : %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=logging.INFO
    )
    if not activate_logs:
        logging.disable()

    archive_with_args = partial(
        archive,
        base_archive_path=base_archive_path,
        process_delay=process_delay
    )
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive_with_args),
    ])
    web.run_app(app)
