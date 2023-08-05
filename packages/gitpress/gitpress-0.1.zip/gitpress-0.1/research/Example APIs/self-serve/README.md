Self Serve
==========

A [Gitpress][gitpress] example that pulls in [a blog repository][blog] and
serves it with [Flask][flask].

To run locally,

    git clone git@github.com:joeyespo/gitpress.git
    cd gitpress/examples/self-serve
    pip install -r requirements.txt
    python self_serve.py

Then visit [http://localhost:8080][localhost] in your browser. The blog content
will automatically be pulled in and served, showing all the git activity in the
console window.

[gitpress]: https://github.com/joeyespo/gitpress
[blog]: https://github.com/joeyespo/gitpress/tree/tree/simple-blog
[flask]: http://flask.pocoo.org/
[local]: http://localhost:8080/
