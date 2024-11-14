import http.client, ssl, urllib.parse
from config import logger

def get_https(host, url, max_redirects=1):
    sslcontext = ssl.create_default_context()
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    try:
        conn = http.client.HTTPSConnection(host=host, context=sslcontext)
        conn.request(method="GET", url=url)
        response = conn.getresponse()
        if response.status == 301 and max_redirects > 0:
            location = response.getheader("Location")
            conn.close()
            parsed_url = urllib.parse.urlparse(location)
            return get_https(
                host=parsed_url.netloc,
                url=parsed_url.path + "?" + parsed_url.query,
                max_redirects=max_redirects - 1,
            )
        elif max_redirects == 0:
            logger.error("get_https() max redirection reached...")
            return None
        data = response.read()
        conn.close()
        return data.decode()
    except Exception as e:
        logger.error(f"get_https() Exception: {e}")
        return None