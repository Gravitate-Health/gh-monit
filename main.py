import socket
import time
import requests
import os

# Configuration
GRAPHITE_HOST = os.getenv(
    "GRAPHITE_HOST", "127.0.0.1"
)  # "host.docker.internal"  # Replace with your Graphite host
GRAPHITE_PORT = os.getenv(
    "GRAPHITE_PORT", 2003
)  # Default port for Carbon plaintext protocol
WEBSITE_URLS = [
    {
        "url": "https://fosps.gravitatehealth.eu/focusing/focus/bundlepackageleaflet-es-94a96e39cfdcd8b378d12dd4063065f9?preprocessors=preprocessing-service-manual&patientIdentifier=alicia-1&lenses=lens-selector-mvp2_pregnancy",
        "desc": "focusing.biktarvy.alicia.pregnancy",
    },
    {
        "url": "https://fosps.gravitatehealth.eu/focusing/focus/bundlepackageleaflet-es-925dad38f0afbba36223a82b3a766438?preprocessors=preprocessing-service-manual&patientIdentifier=alicia-1&lenses=lens-selector-mvp2_pregnancy",
        "desc": "focusing.calcio.alicia.pregnancy",
    },
    {
        "url": "https://fosps.gravitatehealth.eu/focusing/focus/bundlepackageleaflet-es-2f37d696067eeb6daf1111cfc3272672?preprocessors=preprocessing-service-manual&patientIdentifier=alicia-1&lenses=lens-selector-mvp2_pregnancy",
        "desc": "focusing.tegretol.alicia.pregnancy",
    },
    {
        "url": "https://fosps.gravitatehealth.eu/focusing/focus/bundlepackageleaflet-es-4fab126d28f65a1084e7b50a23200363?preprocessors=preprocessing-service-manual&patientIdentifier=alicia-1&lenses=lens-selector-mvp2_pregnancy",
        "desc": "focusing.xenical.alicia.pregnancy",
    },
    {
        "url": "https://fosps.gravitatehealth.eu/focusing/focus/bundlepackageleaflet-es-29436a85dac3ea374adb3fa64cfd2578?preprocessors=preprocessing-service-manual&patientIdentifier=alicia-1&lenses=lens-selector-mvp2_pregnancy",
        "desc": "focusing.hypericum.alicia.pregnancy",
    },
    {
        "url": "https://fosps.gravitatehealth.eu/focusing/focus/bundlepackageleaflet-es-04c9bd6fb89d38b2d83eced2460c4dc1?preprocessors=preprocessing-service-manual&patientIdentifier=alicia-1&lenses=lens-selector-mvp2_pregnancy",
        "desc": "focusing.flucelvax.alicia.pregnancy",
    },
]


def send_to_graphite(metric_path, value, timestamp=None):
    """
    Sends a metric to Graphite.
    """
    timestamp = timestamp or int(time.time())
    message = f"{metric_path} {value} {timestamp}\n"
    print(f"Sending to Graphite: {message}", end="")

    # Open a socket to Graphite and send the data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((GRAPHITE_HOST, int(GRAPHITE_PORT)))
        sock.sendall(message.encode("utf-8"))


def check_website_status(url):
    """
    Checks the status code of a website.
    """
    try:
        response = requests.post(url)
        return response.status_code
    except requests.RequestException as e:
        print(f"Error checking website status: {e}")
        return None


def main():
    while True:
        for WEBSITE_DATA in WEBSITE_URLS:
            WEBSITE_URL = WEBSITE_DATA["url"]
            WEBSITE_DESC = WEBSITE_DATA["desc"]
            status_code = check_website_status(WEBSITE_URL)
            if status_code is not None:
                metric_path = f"gh.{WEBSITE_DESC}"
                send_to_graphite(metric_path, status_code)
        # time.sleep(3600)
        time.sleep(1800)


if __name__ == "__main__":
    main()
