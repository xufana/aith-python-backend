import json
import math
from typing import Any, Awaitable, Callable, List, Dict
from urllib.parse import parse_qs

async def app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
    
    if scope["method"] != "GET":
        content, status_code = {"error": "Not Found"}, 404
        await send_response(send, content, status_code)
        return
    
    path = scope["path"]
    method = scope["method"]
    query_string = scope["query_string"].decode("utf-8")
    query_params = parse_qs(query_string)

    if path == "/factorial":
        n_str = query_params.get("n", [None])[0]

        if not n_str:
            content, status_code = {"error": "Parameter n is required"}, 422
            await send_response(send, content, status_code)
            return
        try:
            n = int(n_str)
        except:
            content, status_code = {"error": "n must be an integer"}, 422
            await send_response(send, content, status_code)
            return
        
        if n < 0:
            content, status_code = {"error": "n must be non-negative"}, 400
            await send_response(send, content, status_code)
            return
        else:
            factorial = math.factorial(n)
            content, status_code = {"result": factorial}, 200
            await send_response(send, content, status_code)
            return
        
    elif path.startswith("/fibonacci"):
        path_parts = path.split("/")

        try:
            n = int(path_parts[-1])
        except:
            content, status_code = {"error": "n must be an integer"}, 422
            await send_response(send, content, status_code)
            return
        
        if n < 0:
            content, status_code = {"error": "n must be non-negative"}, 400
            await send_response(send, content, status_code)
            return
        else:
            a, b = 0, 1
            for _ in range(n):
                a, b = b, a + b
            fibonacci = b
            content, status_code = {"result": fibonacci}, 200
            await send_response(send, content, status_code)
            return
        
    elif path.startswith("/mean"):
        body = await receive()

        try:
            array = json.loads(body["body"])
        except:
            content, status_code = {"error": "Request body must be valid JSON"}, 422
            await send_response(send, content, status_code)
            return
        
        if not isinstance(array, list):
            content, status_code = {"error": "Request body must be an array"}, 422
            await send_response(send, content, status_code)
            return
        if len(array) == 0:
            content, status_code = {"error": "Array must be not empty"}, 400
            await send_response(send, content, status_code)
            return
        
        try:
            float_array = [float(x) for x in array]
        except:
            content, status_code = {"error": "All elements must be float numbers"}, 422
            await send_response(send, content, status_code)
            return
        
        mean_val = sum(float_array) / len(float_array)
        content, status_code = {"result": mean_val}, 200
        await send_response(send, content, status_code)
        return
    
    await send_response(send, content={"error": "Not Found"}, status_code=404)


async def send_response(send, content, status_code):
    response = json.dumps(content).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                [b"content-type", b"application/json"],
            ],
        }
    )
    await send({"type": "http.response.body", "body": response})

