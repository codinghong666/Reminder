from fastapi import FastAPI
import sduwrap
from sduwrap import ChatConfig

from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import uuid
import time

app = FastAPI()

app.add_middleware(
     CORSMiddleware,
     allow_origins=["*"],  # 根据需求调整允许的源
     allow_credentials=True,
     allow_methods=["POST", "OPTIONS"],  # 明确允许 OPTIONS 和 POST
     allow_headers=["*"],  # 允许所有头
 )

# 假设这是用户已有的生成器函数（需自行实现具体逻辑）
def chat(content: str, history: list, config: ChatConfig) -> str:
    request_history = []
    for chat_session in history:
        cs = sduwrap.ChatSession()
        cs.role = chat_session["role"]
        cs.content = chat_session["content"]

        request_history.append(cs)

    for response in sduwrap.chat(content, request_history, config):
        yield response


@app.post("/v1/chat/completions")
async def openai_chat_completion(request: Request):
    # 解析请求体
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    # 提取必要参数
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    model = body.get("model", "deepseek_reasoner_web")  # 模型名称按需处理

    config = ChatConfig()

    model_config = {
        "deepseek_reasoner_web": (73, "本科生", 1, 1),
        "deepseek_reasoner": (73, "本科生", 1, 2),
        "deepseek_web": (73, "本科生", 2, 1),
        "deepseek": (73, "本科生", 2, 2),
        "QwQ": (72, "本科生", 2, 2),
        "QwQ_web": (72, "本科生", 2, 1),
        "QwQ_reasoner": (72, "本科生", 1, 2),
        "QwQ_reasoner_web": (72, "本科生", 1, 1),
    }

    if model in model_config:
        config.compose_id, config.auth_tag, config.deep_search, config.internet_search = model_config[model]

    # 校验消息格式
    if not messages or messages[-1]["role"] != "user":
        raise HTTPException(status_code=400, detail="Invalid messages format")

    # 提取当前输入和历史记录
    current_input = messages[-1]["content"]
    history = messages[:-1]  # 按需调整历史处理逻辑

    # 流式响应处理
    if stream:
        def generate_stream():
            # 生成唯一响应ID
            response_id = f"sdu_ds-{uuid.uuid4()}"
            created = int(time.time())

            # 遍历生成器生成事件流
            for chunk in chat(current_input, history, config):
                event_data = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(event_data)}\n\n"

            # 结束事件
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )

    # 非流式响应处理
    else:
        # 收集完整响应
        full_response = "".join([
            chunk for chunk in chat(current_input, history, config)
        ])

        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": full_response
                },
                "finish_reason": "stop"
            }],
            "usage": {  # 按需实现实际token计算
                "prompt_tokens": len(current_input),
                "completion_tokens": len(full_response),
                "total_tokens": len(current_input) + len(full_response)
            }
        }


if __name__ == "__main__":
    # 判断 ./cookies.json 是否存在
    try:
        with open("./cookies.json", "r") as f:
            sduwrap.cookies = json.load(f)
            if not sduwrap.cookies:
                raise FileNotFoundError
    except FileNotFoundError:
        import sdu_aiassist_login as login
        import getpass
        print("There is no cookies.json file, logging in...")
        sdu_id = input("Please enter your SDU ID: ")
        password = getpass.getpass("Please enter your password: ")
        # fingerprint = input("Please enter your fingerprint(Any String For Generate Random UUID): ")
        # try read fingerprint from file
        try:
            with open("./fingerprint.txt", "r") as f:
                fingerprint = f.read().strip()
        except FileNotFoundError:
            # generate random uuid
            fingerprint = input("Please enter your fingerprint(Empty to generate one): ")
            if not fingerprint:
                fingerprint = str(uuid.uuid4())
            with open("./fingerprint.txt", "w") as f:
                f.write(fingerprint)
        fingerprint = str(uuid.uuid5(uuid.NAMESPACE_URL, fingerprint))

        cookies = login.login(sdu_id, password, fingerprint)["cookies"]
        if not cookies:
            raise Exception("Login failed")

        sduwrap.cookies = cookies

        with open("./cookies.json", "w") as f:
            json.dump(cookies, f)

    uvicorn.run(app, host="0.0.0.0", port=8000)
