from flask import Flask, request, jsonify, render_template
import time
import json
import websocket

app = Flask(__name__)

def llm_generate_nostream(gen_prompt="", gen_temp=0.55, gen_top_p=1, gen_top_k=50, gen_repetition_penalty=1.05, gen_max_new_tokens=32768, gen_stop_strings=[]):
    ws = websocket.create_connection("ws://localhost:5005/")
    params = {
        'gen_prompt': gen_prompt,
        'gen_temp': gen_temp,
        'gen_top_p': gen_top_p,
        'gen_top_k': gen_top_k,
        'gen_repetition_penalty': gen_repetition_penalty,
        'gen_max_new_tokens': gen_max_new_tokens,
        'gen_stop_strings': gen_stop_strings,
        'stream': False
    }
    ws.send(json.dumps(params))
    result = ws.recv()
    ws.close()
    return result


def build_prompt(query):
    website_template = f"""Generate a website containing content for {query}. Use only inline css and don't insert images. Be creative!

Generated HTML Website:
<body>
""" 
    return website_template


def generate_website(query):
    prompt = build_prompt(query)
    website_html = llm_generate_nostream(gen_prompt=prompt, gen_stop_strings=["</body>", "</script>"])
    return website_html

@app.route('/navigate')
def navigate():
    url = request.args.get('url')
    query_text = request.args.get('query')
    print("URL:", url)
    print("Query:", query_text)
    try:
        generated_html = generate_website(query_text)
        return generated_html
    except Exception as e:
        return f"<html><body><p>Error: {str(e)}</p></body></html>"

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=21124)