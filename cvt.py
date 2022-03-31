# 别称转换
import json
import umamusume_bot

# 图片转换
from PIL import Image
im = Image.open("tt.png")

data = im.load()
w, h = im.size

for i in range(w):
    for n in range(h):
        print(data[i, n])

exit()
# 图片转换结束

with open("./umamusume_bot/data/uma_alias.json", encoding="utf8") as f:
    data_alias = json.load(f)

uma_db = umamusume_bot.load_db("./pretty-derby/src/assert/db.json")
new_trans = {}

for umas in uma_db.players:
    card_name = umas.name
    char_name = umas.charaName

    if char_name not in new_trans:
        new_trans[char_name] = {}

    new_trans[char_name][card_name] = data_alias[char_name]

print(json.dumps(new_trans, ensure_ascii=False))
