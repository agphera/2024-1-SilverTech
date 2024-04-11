import urllib
from karlo import make_prompt, t2i
from PIL import Image

""" 
subject: "mountain1", "mountain2", "park1", "park2", "sky1", "sky2"
final-subject: "stream1", "stream2", "farming1", "farming2"
"""
subject = "sky"
prompt = make_prompt(subject)
print(prompt)

response = t2i(prompt)
result = Image.open(urllib.request.urlopen(response.get("images")[0].get("image")))
result.show()