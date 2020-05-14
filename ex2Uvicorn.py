import asyncio
import urllib.parse
from bareasgi import (
    Application,
    text_reader,
    text_writer
    )
import uvicorn

# Change an event - Do something asynchronous
async def get_index(scope, info, matches, content):
    try:
        await asyncio.wait_for(info['event'].wait(), timeout=0.1)
    except asyncio.TimeoutError:
        pass
text = """
<html>
    <body>
        <button onclick="changeEvent('{state}')">{message}</button>
        <script>
            function changeEvent(state) {{
                fetch('/change_event', {{ method: 'POST', body: state }})
                    .then(response => location.reload())
            }}
        </script>
    </body>
</html>
""".format(
    message='Clear' if info['event'].is_set() else 'Set',
    state='False' if info['event'].is_set() else 'True'
    )
    return 200, [(b'content-type', b'text/html')], text_writer(text)

async def change_event(scope, info, matches, content):
    if await text_reader(content) == 'True':
        info['event'].set()
    else:
        info['event'].clear()
    return 204

# !!! Create the event !!!
event = asyncio.Event()
app = Application(info={'event': event})
app.http_router.add({'GET'}, '/', get_index)
app.http_router.add({'POST'}, '/change_event', change_event)

uvicorn.run(app, port=9009, loop='auto')
