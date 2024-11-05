import asyncio
from shadowserver.main import ShadowServer


server = ShadowServer("https://www.google.com/")

if __name__ == "__main__":
    asyncio.run(server.start_server())