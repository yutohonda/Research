import easyocr
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import matplotlib.patches as patches
import japanize_matplotlib

image_path = "test.png"
reader = easyocr.Reader(['ja','en'],gpu = True) # this needs to run only once to load the model into memory
result = reader.readtext(image_path)
print("==========検出結果===========")

image = Image.open(image_path)

fig = plt.figure(figsize = (40,40))
ax = plt.axes()
ax.imshow(image)
ax.axis("off")
for t in result:
    try:
        bbox = np.array(t[0])
        print(t[1])
        ax.text(bbox[0,0], bbox[0,1], t[1], size=30, fontname="MS Gothic",color="black")
        r = patches.Rectangle(xy=(bbox[0,0], bbox[0,1]), width=(bbox[2,0] - bbox[0,0]), height=(bbox[2,1] - bbox[0,1]), ec='g', fill=False,linewidth='10.0')
        ax.add_patch(r)
    except:
        continue
plt.savefig('./result.png')