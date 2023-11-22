import googletrans 
from googletrans import Translator

#print(googletrans.LANGUAGES)
translator = Translator()

result = translator.translate('how much time in museum', dest ='hi')
print(result.src)
print(result.dest)
print(type(result.src))
print(type(result.dest))
res = str(result.dest)
print(res)
print(result.origin)
print(result.text)
print(result.pronunciation)
a = 10
b = 2

print(a+b)