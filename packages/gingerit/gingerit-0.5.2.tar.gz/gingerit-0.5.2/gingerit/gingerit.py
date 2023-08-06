import requests


class GingerIt:
    def __init__(self):
        self.url = 'http://services.gingersoftware.com/Ginger/correct/json/GingerTheText'
        self.api_key = '6ae0c3a0-afdc-4532-a810-82ded0054236'
        self.api_version = '2.0'
        self.lang = 'US'

    def parse(self, text):
        s = requests.Session()
        req = s.get(
            self.url,
            params={
                'lang': self.lang,
                'apiKey': self.api_key,
                'clientVersion': self.api_version,
                'text': text
            },
        )
        data = req.json()
        return self.process_data(text, data)

    def process_data(self, text, data):
        result = ''
        corrections = []
        i = 0

        for suggestion in data['LightGingerTheTextResult']:
            start = suggestion["From"]
            end = suggestion["To"]

            if i <= end:
                if start != 0:
                    result += text[i:start-1]
                result += " " + suggestion['Suggestions'][0]['Text']

                corrections.append({
                    'text': text[start:end],
                    'correct': suggestion['Suggestions'][0].get('Text', None),
                    'definition': suggestion['Suggestions'][0].get('Definition', None)
                })

            i = end + 1

        if i < len(text):
            result += text[i:-1]
        return {'text': text, 'result': result, 'corrections': corrections}
