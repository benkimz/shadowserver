# ShadowServer

`shadowserver` is an asynchronous HTTP/HTTPS proxy server library built using `aiohttp`, designed to forward requests from clients to a target server. It efficiently handles HTTP and WebSocket connections, provides CORS support, and allows custom SSL certificates. `shadowserver` is ideal for proxying requests to backend services or simulating server requests for testing and development purposes.

## Features

- **HTTP and HTTPS Proxying**: Supports both HTTP and HTTPS requests.
- **CORS Support**: Cross-Origin Resource Sharing (CORS) headers are automatically managed to allow cross-origin requests.
- **WebSocket Support**: Forwards WebSocket connections between client and server.
- **Custom SSL Certificates**: Accepts paths to custom SSL certificates for secure HTTPS connections.
- **Asynchronous Design**: Uses `aiohttp` to handle concurrent requests asynchronously.

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
    proxy = ShadowServer(target_base_url="https://example.com", timeout=30, max_conn=100)

    # Start the server
    await proxy.start_server(host="127.0.0.1", port=8080)

# Run the server
asyncio.run(main())
```

### Using Custom SSL Certificates

To specify a custom SSL certificate and key, pass the paths as arguments when starting the server:

```python
await proxy.start_server(host="127.0.0.1", port=8080, ssl_cert_path="/path/to/cert.pem", ssl_key_path="/path/to/key.pem")
```

---

## ShadowServer URL Redirection

The `ShadowServer` class now supports an optional redirect feature, allowing users to automatically redirect requests from the base URL to a specified target URL. This feature can be enabled by passing a `redirect_url` and setting the `redirects` parameter to `True` when initializing the server.

### Parameters

- **redirect_url**: `str`  
  The URL to redirect to when the base URL (i.e., `/`) is accessed. This parameter is optional but required if `redirects` is set to `True`.
- **redirects**: `bool`  
  If `True`, requests to the base URL will be redirected to the URL specified in `redirect_url`. If `False`, all requests are proxied to `target_base_url` without redirection.

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
    port=3000,
    cert_path="./cert/localhost.crt",
    key_path="./cert/localhost.key"
))
```

In this setup:

- Any request to `http://127.0.0.1:3000/` (the base URL) will automatically be redirected to `https://example.com/home`.
- All other requests (e.g., `http://127.0.0.1:3000/some/path`) will be proxied to `https://example.com/api/some/path`.

#### Example 2: Disabling Redirection

If you want to use `ShadowServer` as a traditional proxy without redirection, simply omit `redirect_url` and set `redirects=False` (or leave it as the default):

```python
from shadowserver import ShadowServer
import asyncio

BASE_URL = "https://example.com/api"

server = ShadowServer(
    target_base_url=BASE_URL,
    redirects=False  # No redirection, acts as a normal proxy
)

asyncio.run(server.start_server(
    host="127.0.0.1",
    port=3000,
    cert_path="./cert/localhost.crt",
    key_path="./cert/localhost.key"
))
```

In this configuration:

- Requests to `http://127.0.0.1:3000/` will be proxied to `https://example.com/api/`, with no redirection.

### Redirect Behavior

When `redirects=True` and a `redirect_url` is provided, any request to the base URL will return a `302 Found` response, redirecting the client to the `redirect_url`. This is useful for scenarios where you want to guide users from the proxy’s root path to a specific target.

---

### Notes

- The `redirect_url` parameter must be a fully qualified URL (e.g., `https://example.com/home`).
- Only requests to the exact base URL (`/`) will trigger the redirect.

## API Reference

### ShadowServer

The main class that sets up and runs the proxy server.

```python
class ShadowServer:
    def __init__(self, target_base_url, timeout=30, max_conn=100)
```

- **Parameters**:
  - `target_base_url` (str): The base URL to which all proxied requests are forwarded.
  - `timeout` (int, optional): Timeout in seconds for requests to the target server. Default is `30`.
  - `max_conn` (int, optional): Maximum number of concurrent connections. Default is `100`.

#### Methods

1. **`start_server`**

   ```python
   async def start_server(self, host='127.0.0.1', port=8080, ssl_cert_path=None, ssl_key_path=None)
   ```

   Starts the proxy server.

   - **Parameters**:

     - `host` (str, optional): The host IP on which the server runs. Default is `'127.0.0.1'`.
     - `port` (int, optional): The port on which the server listens. Default is `8080`.
     - `ssl_cert_path` (str, optional): Path to the SSL certificate file.
     - `ssl_key_path` (str, optional): Path to the SSL key file.

   - **Example**:

     ```python
     await proxy.start_server(host='127.0.0.1', port=8080, ssl_cert_path='cert.pem', ssl_key_path='key.pem')
     ```

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

## Advanced Configuration

### Setting Custom Headers

By default, `shadowserver` removes specific headers such as `Host` and CORS headers from the client request before forwarding them. You can add additional headers by modifying the `prepare_headers` function.

### Setting Timeout and Maximum Connections

You can set custom timeout and connection limits during initialization:

```python
proxy = ShadowServer(target_base_url="https://example.com", timeout=60, max_conn=200)
```

This will set a 60-second timeout and allow up to 200 concurrent connections.

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License.

---

## Troubleshooting

### CORS Errors

If you encounter CORS issues, ensure that the client request headers include the correct `Origin`.

### SSL Errors

For HTTPS proxying, make sure the SSL certificate paths are correct, or the proxy will only handle HTTP requests.

---

This documentation should help you get started with `shadowserver` and provide a quick reference for common usage patterns and configurations.
