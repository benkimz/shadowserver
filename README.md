# ShadowServer

`shadowserver` is an asynchronous HTTP proxy server library using `aiohttp`, designed to forward requests from clients to a target server. It handles HTTP and WebSocket connections, provides CORS support, and offers flexible SSL verification options, making it ideal for backend service proxying and server simulations in testing environments.

## Features

- **HTTP Proxying**: Supports forwarding HTTP requests to a specified target.
- **CORS Support**: Automatically adds headers to enable cross-origin requests.
- **WebSocket Support**: Forwards WebSocket connections between client and target server.
- **Flexible SSL Verification**: Allows disabling SSL verification for outgoing HTTPS requests.
- **Route Support**: Ability to append a custom route to the proxy server URL.
- **Asynchronous Design**: Built with `aiohttp` for handling multiple concurrent requests efficiently.

---

## Installation

You can install `shadowserver` via pip:

```bash
pip install shadowserver
```

---

## Usage

Below is a basic example of how to set up and run `shadowserver`.

### Basic Example

```python
from shadowserver import ShadowServer
import asyncio

async def main():
    # Initialize the server with the target URL and optional settings
    proxy = ShadowServer(
        target_base_url="https://example.com",
        timeout=30,
        max_conn=100,
        open_on_browser=True,
        verify_ssl=True
    )

    # Start the server
    await proxy.start_server(host="127.0.0.1", port=8080)

# Run the server
asyncio.run(main())
```

### Disabling SSL Verification

To disable SSL verification for outgoing HTTPS requests, pass `verify_ssl=False` during initialization:

```python
proxy = ShadowServer(
    target_base_url="https://example.com",
    verify_ssl=False  # Disables SSL verification for HTTPS requests
)
```

This can be useful for development environments where the target server uses a self-signed certificate.

---

## ShadowServer URL Redirection

The `ShadowServer` class includes an optional redirect feature to automatically redirect requests from the base URL to a specified URL. This is enabled by passing a `redirect_url` and setting `redirects=True`.

### Parameters

- **redirect_url**: `str`  
  The URL to redirect to when the base URL (`/`) is accessed.
- **redirects**: `bool`  
  Enables or disables the redirect from the base URL to `redirect_url`.

### Example Usage

Here are some examples showing how to configure the `ShadowServer` with URL redirection.

#### Example 1: Redirecting Requests from Base URL to Another URL

In this example, requests to the base URL (`/`) will be redirected to the URL specified in `redirect_url`:

```python
from shadowserver import ShadowServer
import asyncio

BASE_URL = "https://example.com/api"
REDIRECT_URL = "https://example.com/home"

server = ShadowServer(
    target_base_url=BASE_URL,
    redirect_url=REDIRECT_URL,
    redirects=True
)

asyncio.run(server.start_server(
    host="127.0.0.1",
    port=3000
))
```

- Requests to `http://127.0.0.1:3000/` will automatically redirect to `https://example.com/home`.
- All other requests (e.g., `http://127.0.0.1:3000/some/path`) will be proxied to `https://example.com/api/some/path`.

#### Example 2: Disabling Redirection

To use `ShadowServer` as a proxy without redirection, omit `redirect_url` and set `redirects=False`:

```python
from shadowserver import ShadowServer
import asyncio

BASE_URL = "https://example.com/api"

server = ShadowServer(
    target_base_url=BASE_URL,
    redirects=False  # Disables redirection
)

asyncio.run(server.start_server(
    host="127.0.0.1",
    port=3000
))
```

---

## Advanced Configuration

### Setting a Custom Route

You can specify a custom route that will be appended to the base URL. This is useful when you want the server to be accessible via a specific route.

```python
proxy = ShadowServer(
    target_base_url="https://example.com",
    route="/customroute"
)

asyncio.run(proxy.start_server(host="127.0.0.1", port=8080))
```

### Setting Timeout and Maximum Connections

To configure custom timeouts and connection limits during initialization:

```python
proxy = ShadowServer(target_base_url="https://example.com", timeout=60, max_conn=200)
```

This example sets a 60-second timeout and allows up to 200 concurrent connections.

---

## API Reference

### ShadowServer

The main class for setting up and running the proxy server.

```python
class ShadowServer:
    def __init__(self, target_base_url, timeout=30, max_conn=100)
```

- **Parameters**:
  - `target_base_url` (str): The base URL to which all proxied requests are forwarded.
  - `timeout` (int, optional): Timeout in seconds for requests to the target server. Default is `30`.
  - `max_conn` (int, optional): Maximum number of concurrent connections. Default is `100`.
  - `redirect_url` (str, optional): URL for redirecting requests from the base URL.
  - `redirects` (bool, optional): If `True`, enables redirection to `redirect_url`. Default is `False`.
  - `open_on_browser` (bool, optional): Automatically opens the server URL in a browser when started. Default is `True`.
  - `verify_ssl` (bool, optional): If `False`, disables SSL verification. Default is `True`.
  - `route` (str, optional): Appends a custom route to the server URL.

#### Methods

1. **`start_server`**

   ```python
   async def start_server(self, host='127.0.0.1', port=8080)
   ```

   Starts the proxy server.

   - **Parameters**:

     - `host` (str, optional): The host IP on which the server runs. Default is `'127.0.0.1'`.
     - `port` (int, optional): The port on which the server listens. Default is `8080`.

2. **`close`**

   ```python
   async def close(self)
   ```

   Closes the server session and frees up resources.

---

## Request Handling

The `ShadowServer` proxy server processes requests as follows:

1. **handle_request**: Forwards HTTP and HTTPS requests to the target server and returns the response to the client.
2. **handle_websocket**: Forwards WebSocket connections to the target server.
3. **build_response**: Builds the response, applies custom headers (such as CORS), and sends it to the client.

### Example of Proxying a GET Request

Once the server is running, you can make a GET request to any endpoint available on the target server:

```bash
curl http://127.0.0.1:8080/api/resource
```

This request will be proxied to `https://example.com/api/resource`.

### WebSocket Proxying

The proxy supports WebSocket connections. You can connect to the WebSocket server via the proxy as shown below:

```python
import websockets
import asyncio

async def connect():
    uri = "ws://127.0.0.1:8080/socket"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello, World!")
        response = await websocket.recv()
        print(response)

asyncio.run(connect())
```

---

## Troubleshooting

### CORS Errors

If you encounter CORS issues, ensure that the client request headers include the correct `Origin`.

### SSL Verification Errors

To disable SSL verification, set `verify_ssl=False` when initializing the server.
