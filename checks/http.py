import requests

def test_http(url="http://google.com"):
    """Testa se HTTP funciona."""
    try:
        response = requests.get(url, timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False
    except Exception:
        return False
