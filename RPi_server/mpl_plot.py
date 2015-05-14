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
  <option value="day" selected="selected">day</option>
  <option value="week">week</option>
  <option value="month">month</option>
  <option value="year">year</option>
  <option value="all-time">all-time</option>
</select>

<br>

<input type="radio" name="r" value='1'>sensor #1<br> 
<input type="radio" name="r" value='2'>sensor #2<br>
<input type="radio" name="r" value='0' checked="checked">all sensors<br>

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
        
        plotpoints = 300
        
        ct = time.time()
        data = []
        
        if arg == 'day':
            t_shift = 86400
        elif arg == 'week':
            t_shift = 604800
        elif arg == 'month':
            t_shift = 2678400
        elif arg == 'year':
            t_shift = 31536000
        elif arg == 'all-time':
            t_shift = 315360000
        
        with open('sensor_1.dat', 'r') as f:
            for line in f:
                t = int(float(line.split('\t')[0]))
                s = float(line.split('\t')[1])
                if ct - t < t_shift:
                    data.append([t, s])
                                   
        plt.rcParams['figure.figsize'] = (8.0,4.0)

        if len(data) > plotpoints: # avoid plotting too much points
            delta_data = int(np.ceil(len(data)/(plotpoints - 1)))
            new_data = data[::delta_data]
        else:
            new_data = data
            
        x = [d[0] for d in new_data]
        y = [d[1] for d in new_data]
            
        t_start = datetime.datetime.fromtimestamp(x[0])
        t_end = datetime.datetime.today()

        if arg == 'day':
            t_delta = datetime.timedelta(hours=3) 
            xpticks = [t_start +i*t_delta for i in xrange(9)]
            xvticks = ['{:%H:%M}'.format(i) for i in xpticks]
        elif arg == 'week':
            t_delta = datetime.timedelta(days=1)
            xpticks = [t_start +i*t_delta for i in xrange(9)]
            xpticks = [i.replace(hour=00) for i in xpticks]
            xpticks = [i for i in xpticks if i <= t_end + t_delta]
            xvticks = ['{:%a}'.format(i) for i in xpticks]
        elif arg == 'month':
            t_delta = datetime.timedelta(weeks=1)
            xpticks = [t_start +i*t_delta for i in xrange(6)]
            xpticks = [i.replace(hour=00) for i in xpticks]
            xpticks = [i for i in xpticks if i <= t_end + t_delta]
            xvticks = ['{:%d %b}'.format(i) for i in xpticks]
        elif arg == 'year':
            t_delta = datetime.timedelta(days=30)
            xpticks = [t_start +i*t_delta for i in xrange(14)]
            xpticks = [i.replace(day=1) for i in xpticks]
            xpticks = [i for i in xpticks if i <= t_end + t_delta]
            xvticks = ['{:%b}'.format(i) for i in xpticks] 
        elif arg == 'all-time':
            t_delta = datetime.timedelta(days=365)
            xpticks = [t_start +i*t_delta for i in xrange(9)]
            xpticks = [i.replace(month=1) for i in xpticks]
            xpticks = [i for i in xpticks if i <= t_end + t_delta]
            xvticks = ['{:%Y}'.format(i) for i in xpticks] 
        xpticks = [time.mktime(i.timetuple()) for i in xpticks]
       
        plt.title('Data for ' + '{:%Y-%m-%d}'.format(t_start) + 
                        ' - ' + '{:%Y-%m-%d}'.format(datetime.date.today()))
        plt.plot(x, y, 'b-', linewidth=2, label='sensor_1') 
        plt.xticks(xpticks, xvticks)
        plt.legend(loc=1)
        plt.xlim([xpticks[0], xpticks[-1]])
            
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
