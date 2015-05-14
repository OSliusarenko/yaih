import tornado.ioloop
import tornado.web

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
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
plot recent:
<select id="ddlViewBy">
  <option value="day">day</option>
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
        ct = time.time()
        data = []
        if arg=='day':
            with open('sensor_1.dat', 'r') as f:
                for line in f:
                    t = int(float(line.split('\t')[0]))
                    s = float(line.split('\t')[1])
                    if ct - t < 86400:
                        data.append([t, s])
                                   
            plt.rcParams['figure.figsize'] = (8.0,4.0)

            if len(data) > 150: # avoid plotting too much points
                delta_data = int(len(data)/149) 
                                   
            new_data = data[::delta_data]
            x = [d[0] for d in new_data]
            y = [d[1] for d in new_data]
            
            t_start = datetime.datetime.fromtimestamp(x[0])
            t_delta = datetime.timedelta(hours=3)
            
            xpticks = [t_start +i*t_delta for i in xrange(9)]
            xvticks = map('{:%H:%M}'.format, xpticks)
            xpticks = [time.mktime(i.timetuple()) for i in xpticks]

            plt.title('Data for ' + '{:%Y-%m-%d}'.format(t_start) + 
                        ' - ' + '{:%Y-%m-%d}'.format(datetime.date.today()))
            plt.plot(x, y, 'b-', linewidth=2, label='sensor_1')            
            plt.xticks(xpticks, xvticks)
            
            plt.legend(loc=1)
            
            io = StringIO()
            plt.savefig(io, format='svg')
            plt.close()
            self.set_header("Content-Type", "image/svg+xml")
            self.write(io.getvalue())



application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/img", ImgHandler),
  (r"/img/(.*)", ImgHandler),
  ])

if __name__ == "__main__":
  application.listen(8080)
  tornado.ioloop.IOLoop.instance().start()
