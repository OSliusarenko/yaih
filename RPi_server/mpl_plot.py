import tornado.ioloop
import tornado.web

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from io import StringIO, BytesIO

html_content = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">

  <html>
<head>
	<title>Sensors Plot</title>
	<script language="JavaScript">
<!--

function Start() {
    var e = document.getElementById("ddlViewBy");
    var strUser = e.options[e.selectedIndex].value;

    var inp = document.getElementsByName('r');
    var i = 0;
    for (i = 0; i < inp.length; i++) {
        if (inp[i].type == "radio" && inp[i].checked) {
            break;
        }
    }

	//alert(strUser + " " + inp[i].value);
	
	window.location = "img/" + strUser;
}

//-->
</script>
</head>

<body text="#000000"  bgcolor="#FFFeea">
<p align="center">
<b>Select what to plot</b> <br> <br>
</p>
<hr width="50%">
<p align="center">
<select id="ddlViewBy">
  <option value="0.5">factor=0.5</option>
  <option value="1" selected="selected">factor=1</option>
  <option value="2">factor=2</option>
</select>

<br>

<input type="radio" name="r" value=0.675>sensor #1<br> 
<input type="radio" name="r" value=0.34>sensor #2<br>
<br><br>
<input type="button" value=" Start " onclick="Start();">
</p>



</body>
</html>
"""

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.write(html_content)

class ImgHandler(tornado.web.RequestHandler):
  def get(self, arg=1):

    arg=float(arg)
    xs = np.linspace(-10, 10, 1000)
    plt.plot(xs, np.sin(xs/arg), label='sin(x)')

    io = StringIO() #io = BytesIO()
    plt.savefig(io, format='svg') #plt.savefig(io, format='png')
    plt.close()
    self.set_header("Content-Type", "image/svg+xml")
    #self.set_header("Content-Type", "png")
    self.write(io.getvalue())

application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/img", ImgHandler),
  (r"/img/(.*)", ImgHandler),
  ])

if __name__ == "__main__":
  application.listen(8080)
  tornado.ioloop.IOLoop.instance().start()
