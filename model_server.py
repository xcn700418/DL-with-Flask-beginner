from flask import Flask, request, jsonify
import base64
import torch
from torchvision import transforms
from PIL import Image
from utils.augmentations import letterbox
from utils.general import non_max_suppression
import numpy as np
from PIL import Image
import io

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
app = Flask(__name__)

# load model
def load_model():
    weigths = torch.load('/path/of/ur/model/weights', map_location=device)
    model = weigths['model']
    model.eval()
    if next(model.parameters()).is_floating_point() and next(model.parameters()).dtype == torch.float16:  
        half = True  
    else:  
        half = False  
    return model, half

def base64ToImage(str):
    encoded = str.encode('raw_unicode_escape') #str转byte
    encoded = base64.b64decode(encoded)
    image_bytes = io.BytesIO(encoded)  
    image = Image.open(image_bytes)  
    rgb_image = image.convert('RGB')
    ndarray_image = np.array(rgb_image)
    return ndarray_image

@app.route('/api', methods=["POST"])
def model_inference():
    params = request.form if request.form else request.json
    name = params.get("name")
    imgData = params.get("imgData")

    #receive rgb image from the client
    rgbimg = base64ToImage(imgData)
    model, is_half = load_model()

    #pre-process image
    image = letterbox(rgbimg, 640, stride=64, auto=True)[0]
    image = transforms.ToTensor()(image)
    image = torch.tensor(np.array([image.numpy()]))
    if is_half:
        image = image.half()
    image = image.to(device)

    # predict
    output = model(image)
    results = non_max_suppression(output[0], conf_thres=0.6, iou_thres = 0.5)
    
    for r in results:
        xyxy = r[:4]

    #visualize the detection box coordinats
    print(xyxy)

    #open("./uploads/saveImage/res.txt", 'wb').write(xyxy)
    return jsonify(content_type='application/json;charset=utf-8',
                   reason='success',
                   charset='utf-8',
                   status='200')

if __name__ == "__main__":
    app.run(host='0.0.0.0',
            threaded=True,
            debug=True,
            port=7777) # 随意指定一个未被占用的端口

