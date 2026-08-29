from flask import Flask, Response, jsonify

from tetra_pi.config import Config
from tetra_pi.state import RSSIState

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TETRA RSSI</title>
<style>
 body { font-family: monospace; background:#111; color:#eee; text-align:center; padding-top:2rem; }
 .bar { width:80%; max-width:600px; height:40px; margin:1rem auto; background:#222; border:1px solid #444; }
 .fill { height:100%; width:0%; background:linear-gradient(90deg,#0f0,#ff0,#f00); transition:width .3s; }
 .val { font-size:1.6rem; }
 span.k { color:#88f; }
</style>
</head>
<body>
<h1>TETRA RSSI</h1>
<div class="val" id="level">--</div>
<div class="bar"><div class="fill" id="fill"></div></div>
<p><span class="k">current</span> <span id="cur">--</span> dB &nbsp;
   <span class="k">floor</span> <span id="floor">--</span> dB &nbsp;
   <span class="k">peak</span> <span id="peak">--</span> MHz</p>
<p><span class="k">scans</span> <span id="scans">0</span></p>
<script>
async function tick(){
  try{
    const r = await fetch('/api/state');
    const s = await r.json();
    const pct = (s.level_normalized*100).toFixed(0);
    document.getElementById('level').textContent = pct + '%';
    document.getElementById('fill').style.width = pct + '%';
    document.getElementById('cur').textContent = s.current_db==null?'--':s.current_db.toFixed(1);
    document.getElementById('floor').textContent = s.noise_floor_db==null?'--':s.noise_floor_db.toFixed(1);
    document.getElementById('peak').textContent = s.peak_freq_hz==null?'--':(s.peak_freq_hz/1e6).toFixed(3);
    document.getElementById('scans').textContent = s.scan_count;
  }catch(e){}
}
setInterval(tick,1000); tick();
</script>
</body>
</html>"""


def create_app(state: RSSIState, config: Config) -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return Response(INDEX_HTML, mimetype="text/html")

    @app.route("/api/state")
    def api_state():
        return jsonify(state.snapshot())

    return app
