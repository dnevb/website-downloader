from functools import lru_cache

from bs4 import BeautifulSoup as BS
from bs4 import element
from tqdm import tqdm
from transformers import AutoTokenizer, MarianMTModel

src = "en"  # source language
trg = "hi"  # target language

model_name = f"Helsinki-NLP/opus-mt-{src}-{trg}"
model = MarianMTModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

@lru_cache(maxsize=2000)
def translate(text):
  inputs = tokenizer([text], return_tensors="pt")
  tokens = model.generate(**inputs, 
                          max_new_tokens=200
                          )
  translation = tokenizer.batch_decode(tokens, skip_special_tokens=True)

  return translation[0]

def tag_visible(el):
  if el.parent.name in [
    'style', 'script', 'head', 'meta', '[document]', 'html']:
    return False
  if not el.strip(): return False
  if isinstance(el, element.Comment):
      return False
  return True

def translate_html(content, name):
  soup = BS(content, 'html.parser')

  if soup.html['lang'] == trg:
    return str(soup)
  

  list = soup.find_all(text=True)
  tag_list = set(filter(tag_visible, list))
  total = len(tag_list)

  for tag in tqdm(tag_list, desc=name, total=total):
    text = tag.strip()
    t = translate(text)
    tag.string.replace_with(t)

  soup.html['lang'] = trg
  return str(soup)
