import aiohttp
import asyncio
import async_timeout
from quart import Quart, jsonify

app = Quart(__name__)

async def fetch(url):
    async with aiohttp.ClientSession() as session, async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

def fight(responses):
    return jsonify([len(r) for r in responses])

@app.route("/")
async def index():
    # perform multiple async requests concurrently
    responses = await asyncio.gather(
        fetch("https://google.com/"),
        fetch("https://bing.com/"),
        fetch("https://duckduckgo.com"),
        fetch("http://www.dogpile.com"),
    )

    # do something with the results
    return fight(responses)

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
