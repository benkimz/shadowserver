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
