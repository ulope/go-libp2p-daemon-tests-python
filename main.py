import asyncio
import logging
import random
from typing import Optional

import click
from anyio import SocketStream
from anyio.exceptions import ClosedResourceError
from libp2p import ID
from p2pclient import Client
from p2pclient.datastructures import StreamInfo
from logging import getLogger

log = getLogger(__name__)


async def handler(stream_info: StreamInfo, socket_stream: SocketStream) -> None:
    log.debug('stream_info %s', stream_info)
    while True:
        try:
            data = await socket_stream.receive_some(1024)
        except ClosedResourceError:
            break
        if not data:
            break
        log.warning("data %s: %s", stream_info.peer_id, data)
        if not data.startswith(b'echo'):
            if random.random() < .9:
                try:
                    await socket_stream.send_all(b'echo' + data)
                except ClosedResourceError:
                    break


async def print_peers(client: Client):
    while True:
        log.debug('peers: %d', len(await client.list_peers()))
        await asyncio.sleep(2)


async def main(target: Optional[str]) -> None:
    client = Client()
    own_id, _ = await client.identify()
    log.debug('id %s', own_id)

    asyncio.create_task(print_peers(client))

    async with client.listen():
        log.info("Listening")
        await client.stream_handler('raiden', handler)

        while True:
            if target:
                peer_info = await client.dht_find_peer(ID.from_base58(target))
                log.debug('found peer %s %s', peer_info.peer_id, peer_info.addrs)
                await client.connect(peer_info.peer_id, peer_info.addrs)
                log.debug('connected')
                stream_info, socket_stream = await client.stream_open(peer_info.peer_id, ['raiden'])
                asyncio.create_task(handler(stream_info, socket_stream))
                log.debug('stream open %s', stream_info)
                for i in range(20):
                    await socket_stream.send_all(f'test{i}'.encode())
                    await asyncio.sleep(.1)
                await socket_stream.close()
                break
            await asyncio.sleep(.2)


@click.command()
@click.option("-t", "--target")
def cli(target: str):
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('p2pclient.DaemonConnector').setLevel(logging.INFO)
    asyncio.run(main(target))


if __name__ == "__main__":
    cli()

