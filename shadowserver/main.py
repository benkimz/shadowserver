import asyncio
import aiohttp
from aiohttp import web, ClientSession, ClientTimeout, ClientError, WSMsgType
from multidict import MultiDict
from urllib.parse import urlsplit
import ssl
import threading
import webbrowser
import sys
import os

# ANSI escape codes for colored terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ShadowServer:
    def __init__(self, target_base_url, timeout=30, max_conn=100, redirect_url=None, redirects=False, open_on_browser=True, verify_ssl=True, route="", debug_mode=False):
        self.target_base_url = target_base_url
        self.redirect_url = redirect_url
        self.redirects = redirects
        self.timeout = timeout
        self.max_conn = max_conn
        self.open_on_browser = open_on_browser
        self.verify_ssl = verify_ssl
        self.route = route
        self.session = None
        self.app = web.Application()
        self.app.router.add_route('*', '/{path_info:.*}', self.handle_request)
        self.restart_event = asyncio.Event()
        self.server_url = ""
        self.browser_opened = False
        self.debug_mode = debug_mode

    async def init_session(self):
        """Initialize the session and connector with the running event loop."""
        # Create SSL context based on verify_ssl flag
        ssl_context = None
        if self.target_base_url.startswith("https://") and not self.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            print(f"{Colors.WARNING}[INFO] SSL verification is disabled for outgoing HTTPS requests.{Colors.ENDC}")

        self.session = ClientSession(
            timeout=ClientTimeout(total=self.timeout),
            connector=aiohttp.TCPConnector(limit=self.max_conn, ssl=ssl_context)
        ) 

    async def handle_request(self, request):
        if self.redirects and request.path == '/':
            return web.HTTPFound(self.redirect_url)

        target_url = self.construct_target_url(request)
        headers = self.prepare_headers(request)
        
        # Handle CORS preflight requests
        if request.method == 'OPTIONS':
            return self.handle_cors_preflight()

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
            print(f"\n{Colors.FAIL}[ERROR] Proxy error to {target_url}: {e}{Colors.ENDC}\n")
            return web.Response(status=502, text="Bad Gateway")

    def handle_cors_preflight(self):
        """Return a response for CORS preflight requests."""
        return web.Response(
            status=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, PUT, DELETE, PATCH',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
            }
        )

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
        headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Type'

        return web.Response(
            status=response.status,
            headers=headers,
            body=body
        )

    def construct_target_url(self, request, route=""):
        path_info = route or request.match_info['path_info']
        target_url = f"{self.target_base_url}/{path_info}".rstrip("/")
        if request.query_string:
            target_url += f"?{request.query_string}"
        return target_url    

    def prepare_headers(self, request):
        headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
        headers.update({
            'Host': urlsplit(self.target_base_url).netloc,
            'X-Real-IP': request.remote,
            'X-Forwarded-For': request.headers.get('X-Forwarded-For', request.remote),
            'X-Forwarded-Proto': request.scheme,
        })
        return headers  

    async def start_server(self, host='127.0.0.1', port=8080):
        await self.init_session()
        runner = web.AppRunner(self.app)
        await runner.setup()

        # Append route if specified
        self.server_url = f"http://{host}:{port}{self.route}"
        site = web.TCPSite(runner, host, port)

        # Logging the server start information
        print(f"{Colors.OKGREEN}[INFO] Starting server on {host}:{port} (HTTP){Colors.ENDC}")
        print(f"{Colors.OKBLUE}[INFO] Server available at {self.server_url}{Colors.ENDC}")

        # Open browser only if open_on_browser is True
        if not self.browser_opened and self.open_on_browser:
            threading.Thread(target=lambda: webbrowser.open(self.server_url)).start()
            self.browser_opened = True

        await site.start()
        print(f"{Colors.WARNING}[ACTION] Press Ctrl+C to stop or type 'r' to restart.{Colors.ENDC}")

        if self.debug_mode:
            await self.wait_for_restart()
        else:
            while True:
                await asyncio.sleep(3600)
        await runner.cleanup()
        await self.close()

    async def close(self):
        await self.session.close()

    async def wait_for_restart(self):
        loop = asyncio.get_event_loop()

        def check_for_restart():
            while not self.restart_event.is_set():
                user_input = input()
                if user_input.strip().lower() == 'r':
                    print(f"{Colors.HEADER}[INFO] Restarting server...{Colors.ENDC}")
                    self.restart_event.set()
                    loop.stop()

        threading.Thread(target=check_for_restart, daemon=True).start()
        
        await self.restart_event.wait()
        os.execv(sys.executable, ['python'] + sys.argv)