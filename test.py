import google.generativeai as genai
genai.configure(api_key="AIzaSyARKbi8gr-3sLsw5KOEsZMUsudHA53sxBA")
for m in genai.list_models():
    print(m.name)