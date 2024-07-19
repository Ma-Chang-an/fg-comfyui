import base64
import urllib
import uuid

import websocket
from flask import Flask, render_template, request
import requests
import json
from PIL import Image
import io

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

prompt_text = """
{
  "1": {
    "inputs": {
      "rmbgmodel": [
        "2",
        0
      ],
      "image": [
        "3",
        0
      ]
    },
    "class_type": "BRIA_RMBG_Zho",
    "_meta": {
      "title": "🧹BRIA RMBG"
    }
  },
  "2": {
    "inputs": {},
    "class_type": "BRIA_RMBG_ModelLoader_Zho",
    "_meta": {
      "title": "🧹BRIA_RMBG Model Loader"
    }
  },
  "3": {
    "inputs": {
      "image": "{image_name}",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "4": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "1",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""

app = Flask(__name__)

# 首页路由，展示上传图片的表单页面
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 检查是否有上传的文件
        if 'file' not in request.files:
            return "未找到上传的文件", 400

        file = request.files['file']

        # 如果用户没有选择文件，浏览器会发送一个空文件
        if file.filename == '':
            return "未选择上传的文件", 400

        # 如果文件存在且是图片格式
        if file and allowed_file(file.filename):
            try:
                # 调用 ComfyUI 服务处理图片
                result_image = process_image(file)
                buffered = io.BytesIO()
                result_image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue())

#                解码为字符串
                img_str = img_str.decode('utf-8')

                # 现在你可以将 img_str 传给 render_template
                return render_template('result.html', result_image=f"data:image/png;base64,{img_str}")
                #return render_template('result.html', result_image=result_image)
            except Exception as e:
                return f"处理图片时发生错误: {str(e)}", 500

    return render_template('index.html')

def upload_image_comfyUi(image_file_data):
    try:
        response = requests.post("http://{}/upload/image".format(server_address), files=image_file_data)
        response.raise_for_status()

        # 解析JSON响应
        data = response.json()
        # 提取filename和subfolder
        filename = data['name']
        subfolder = data['subfolder']
        return {"filename": filename, "subfolder": subfolder}
    except requests.exceptions.HTTPError as err:
        print(f"An HTTP error occurred when upload image to ComfyUI : {err}")
    except KeyError as e:
        print(f"Missing key in the response: {e}")

# 处理上传的图片并调用 ComfyUI 服务
def process_image(image_file):
    # 将文件内容读取为字节流
    image_stream = image_file.read()

    # 创建 FormData 对象
    form_data = {'image': (image_file.filename, image_stream, 'image/jpeg')}

    try:
        # 发送 POST 请求给 ComfyUI 服务
        image_resp = upload_image_comfyUi(form_data)
        image_name = image_resp['filename']
        prompt = json.loads(prompt_text)
        prompt["3"]["inputs"]["image"] = image_name

        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
        images = get_images(ws, prompt)

        for node_id in images:
            for image_data in images[node_id]:
                image = Image.open(io.BytesIO(image_data))
                return image

    except requests.exceptions.RequestException as e:
        raise Exception(f"请求 ComfyUI 服务时发生错误: {str(e)}")

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

# 允许上传的文件类型
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

if __name__ == '__main__':
    app.run(debug=True)
