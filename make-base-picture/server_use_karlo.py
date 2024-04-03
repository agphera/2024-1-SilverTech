import urllib
from karlo_picture_generate import make_prompt, t2i
from PIL import Image


# subject: classroom | park | mountain | beach | room
subject = "sky"
prompt = make_prompt(subject)
print(prompt)

response = t2i(prompt)
result = Image.open(urllib.request.urlopen(response.get("images")[0].get("image")))
result.show()
