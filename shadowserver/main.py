import asyncio
import aiohttp
from aiohttp import web, ClientSession, ClientTimeout, ClientError, WSMsgType
from multidict import MultiDict
from urllib.parse import urlsplit
import ssl

class ShadowServer:
    def __init__(self, target_base_url, timeout=30, max_conn=100):
        self.target_base_url = target_base_url
        self.timeout = timeout
        self.max_conn = max_conn
        self.session = None  # Initialized later in an async context
        self.app = web.Application()
        self.app.router.add_route('*', '/{path_info:.*}', self.handle_request)

    async def init_session(self):
        """Initialize the session and connector with the running event loop."""
        self.session = ClientSession(
            timeout=ClientTimeout(total=self.timeout),
            connector=aiohttp.TCPConnector(limit=self.max_conn, ssl=False)
        )

    async def handle_request(self, request):
        target_url = self.construct_target_url(request)
        headers = self.prepare_headers(request)
        
        try:
            if 'upgrade' in request.headers.get('connection', '').lower():
                return await self.handle_websocket(request, target_url, headers)
            
            async with self.session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=await request.read(),
                cookies=request.cookies
            ) as response:
                return await self.build_response(response)

        except ClientError as e:
            print(f"Proxy error to {target_url}: {e}")
            return web.Response(status=502, text="Bad Gateway")
    
    async def handle_websocket(self, request, target_url, headers):
        async with self.session.ws_connect(target_url, headers=headers) as ws_client:
            ws_server = web.WebSocketResponse()
            await ws_server.prepare(request)

            async def forward(ws_from, ws_to):
                async for msg in ws_from:
                    if msg.type == WSMsgType.TEXT:
                        await ws_to.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_to.send_bytes(msg.data)
                    elif msg.type == WSMsgType.CLOSE:
                        await ws_to.close()

            await asyncio.gather(forward(ws_client, ws_server), forward(ws_server, ws_client))
            return ws_server

    def is_response_chunked(self, response):
        """Check if the response is using chunked transfer encoding."""
        return response.headers.get('Transfer-Encoding', '').lower() == 'chunked'

    async def build_response(self, response):
        body = await response.read()

        # Filter headers to ensure no duplicate Content-Length or Content-Encoding headers
        headers = MultiDict((key, value) for key, value in response.headers.items()
                            if key.lower() not in ('transfer-encoding', 'content-encoding', 'content-length', 'access-control-allow-origin', 'access-control-allow-methods', 'access-control-allow-headers'))

        # Set Content-Length if the response is not chunked
        if not self.is_response_chunked(response):
            headers['Content-Length'] = str(len(body))

        # Add CORS headers to allow all origins and HTTP methods
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        return web.Response(
            status=response.status,
            headers=headers,
            body=body
        )


    def construct_target_url(self, request):
        path_info = request.match_info['path_info']
        target_url = f"{self.target_base_url}/{path_info}"
        if request.query_string:
            target_url += f"?{request.query_string}"
        return target_url

    def prepare_headers(self, request):
        headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
        headers['Host'] = urlsplit(self.target_base_url).netloc
        return headers

    async def close(self):
        await self.session.close()

    async def start_server(self, host='127.0.0.1', port=8080, cert_path=None, key_path=None):
        await self.init_session()
        runner = web.AppRunner(self.app)
        await runner.setup()

        ssl_context = None
        if cert_path and key_path:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)

        site = web.TCPSite(runner, host, port, ssl_context=ssl_context)
        print(f'Starting server on {host}:{port} ({"HTTPS" if ssl_context else "HTTP"})')
        await site.start()
        try:
            while True:
                await asyncio.sleep(3600)  # Keep the server running
        finally:
            await runner.cleanup()
            await self.close()