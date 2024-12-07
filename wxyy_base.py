import httpx

class Winxin:
    def chat(self, text):
        input_dict = {
            "text": f"问题：{text} 回答：",
            "seq_len": 512,
            "topp": 0.5,
            "penalty_score": 1.2,
            "min_dec_len": 2,
            "min_dec_penalty_text": "。 ? ：！"
        }
        response = httpx.post("http://127.0.0.1:8000/api/chat", json=input_dict)
        return response.text


winxin = Winxin()
response = winxin.chat("你好")
print(response)        