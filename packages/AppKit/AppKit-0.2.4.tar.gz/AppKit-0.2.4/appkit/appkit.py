#!/usr/bin/env python
from app import App


app = App(__file__)


@app.route('^/$')
def index():
    return 'hi'

app.run()
