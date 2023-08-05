import StringIO
import pyhacc
import datetime

from flask import Flask, request, render_template, url_for
app = Flask(__name__)

Session = None

def getSession():
    global Session

    if Session is None:
        if app.conn == "sqlite://":
            Session = pyhacc.SessionSource("sqlite://", create_level=2)
        else:
            Session = pyhacc.SessionSource(app.conn)

    return Session

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/reports/<path:classname>", methods=['POST', 'GET'])
def reports(classname):
    import pyhacc.reports as rpt

    rptclass = classname.replace('_', ' ').title().replace(' ', '')
    Klass = getattr(rpt, rptclass)
    myrpt = Klass(getSession())

    d = {}
    for x in myrpt.prompt_order:
        if request.args.has_key(x):
            d[x] = request.args.get(x)

    myrpt.construct(**d)

    output = StringIO.StringIO()

    myrpt.html(output)

    html = output.getvalue()

    # insert jquery
    html = html.replace('</head>', '<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.js" type="text/javascript"></script></head><script>$(function() { $( "#datepicker" ).datepicker();});</script>')

    # insert prompt form
    flds = []
    for x in myrpt.prompt_order:
        a = getattr(Klass, x)
        if a.base_type is datetime.date:
            flds.append('{0}: <input type="text" name="{1}" id="datepicker" value="{2}" />'.format(a.label, x, getattr(myrpt, x)))
        elif a.base_type is bool:
            flds.append('{0}: <input type="checkbox" name="{1}"  value="{2}" />'.format(a.label, x, getattr(myrpt, x)))

    flds.append('<input type="submit" value="refresh" />')

    form = "<form method='get' action='{1}'>{0}</form>".format(''.join(flds), url_for('reports', classname=classname))

    html = html.replace("</h1>", "</h1>" + form)

    return html
