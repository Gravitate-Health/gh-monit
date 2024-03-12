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

print(GRAPHITE_HOST, GRAPHITE_PORT)

LENSES = [
    "lens-selector-mvp2_HIV",
    "lens-selector-mvp2_allergy",
    "lens-selector-mvp2_diabetes",
    "lens-selector-mvp2_interaction",
    "lens-selector-mvp2_intolerance",
    "lens-selector-mvp2_pregnancy",
]

PATIENT_IDS = ["alicia-1", "Cecilia-1", "Pedro-1"]
BUNDLES = [
    {
        "id": "bundlepackageleaflet-es-94a96e39cfdcd8b378d12dd4063065f9",
        "name": "biktarvy",
    },
    {
        "id": "bundlepackageleaflet-es-925dad38f0afbba36223a82b3a766438",
        "name": "calcio",
    },
    {
        "id": "bundlepackageleaflet-es-2f37d696067eeb6daf1111cfc3272672",
        "name": "tegretol",
    },
    {
        "id": "bundlepackageleaflet-es-4fab126d28f65a1084e7b50a23200363",
        "name": "xenical",
    },
    {
        "id": "bundlepackageleaflet-es-29436a85dac3ea374adb3fa64cfd2578",
        "name": "hypericum",
    },
    {
        "id": "bundlepackageleaflet-es-04c9bd6fb89d38b2d83eced2460c4dc1",
        "name": "flucelvax",
    },
    {
        "id": "bundlepackageleaflet-es-49178f16170ee8a6bc2a4361c1748d5f",
        "name": "dovato",
    },
    {
        "id": "bundlepackageleaflet-es-e762a2f54b0b24fca4744b1bb7524a5b",
        "name": "mirtazapine",
    },
    {
        "id": "bundlepackageleaflet-es-da0fc2395ce219262dfd4f0c9a9f72e1",
        "name": "blaston",
    },
    {
        "id": "bundlepackageleaflet-es-da0fc2395ce219262dfd4f0c9a9f72e1",
        "name": "blaston",
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
        for bundleid in BUNDLES:
            for lens in LENSES:
                for pid in PATIENT_IDS:
                    WEBSITE_URL = (
                        "https://fosps.gravitatehealth.eu/focusing/focus/"
                        + bundleid["id"]
                        + "?preprocessors=preprocessing-service-manual&patientIdentifier="
                        + pid
                        + "&lenses="
                        + lens
                    )
                    # WEBSITE_URL = WEBSITE_DATA["url"]
                    #  WEBSITE_DESC = WEBSITE_DATA["desc"]
                    status_code = check_website_status(WEBSITE_URL)
                    if status_code is not None:
                        metric_path = f"""gh.focusing.{bundleid["name"]}.{pid}.{lens}"""
                        send_to_graphite(metric_path, status_code)
        # time.sleep(3600)
        time.sleep(600)


if __name__ == "__main__":
    main()
