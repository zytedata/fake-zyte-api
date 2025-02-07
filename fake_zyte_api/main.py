import sys

from aiohttp import web

from .api import handle_request

routes = web.RouteTableDef()


@routes.get("/extract")
async def extract(request: web.Request) -> web.Response:
    req_data = await request.json()
    resp_data = handle_request(req_data)
    return web.json_response(resp_data)


if __name__ == "__main__":
    if len(sys.argv) != 1:
        print(f"Usage: {sys.argv[0]} <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    print(f"Endpoint: http://127.0.0.1:{port}/extract")
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=port)
