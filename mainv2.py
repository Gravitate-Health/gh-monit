import socket
import time
import requests
import os
import json

# Configuration
GRAPHITE_HOST = os.getenv(
    "GRAPHITE_HOST", "127.0.0.1"
)  # "host.docker.internal"  # Replace with your Graphite host
GRAPHITE_PORT = os.getenv(
    "GRAPHITE_PORT", 2003
)  # Default port for Carbon plaintext protocol

BASE_URL = os.getenv("BASE_URL", "https://gravitate-health.lst.tfo.upm.es/")
print(GRAPHITE_HOST, GRAPHITE_PORT)

LENSES = [
    "lens-selector-mvp2_HIV",
    "lens-selector-mvp2_allergy",
    "lens-selector-mvp2_diabetes",
    "lens-selector-mvp2_interaction",
    "lens-selector-mvp2_intolerance",
    "lens-selector-mvp2_pregnancy",
]

# LENSES = requests.post(BASE_URL + "/focusing/lenses")


def log_result(
    status_code,
    warnings,
    method,
    logger_method="file",
    timestamp=None,
    bundleid=None,
    lens=None,
    pid=None,
):
    """
    Sends a metric to Graphite.
    """
    metric_path = f"""gh.{method}.focusing.{bundleid["name"]}.{pid}.{lens}"""
    timestamp = timestamp or int(time.time())
    if status_code == 200 and not warnings:
        value = 1
    else:
        value = 0
        print(status_code, warnings)
    message = f"{metric_path} {value} {timestamp}\n"
    print(f"Sending to Graphite: {message}", end="")
    if logger_method == "graphite":
        # Open a socket to Graphite and send the data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((GRAPHITE_HOST, int(GRAPHITE_PORT)))
            sock.sendall(message.encode("utf-8"))
    else:
        # print(f"Logging to file: {message}")
        with open("focusing_metrics.log", "a") as f:
            f.write(message)


# print(LENSES)
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


def chek_preprocessor_data(BUNDLES, LENSES, PATIENT_IDS, BASE_URL):
    for bundleid in BUNDLES:
        for lens in LENSES:
            for pid in PATIENT_IDS:
                WEBSITE_URL = (
                    BASE_URL
                    + "focusing/focus/"
                    + bundleid["id"]
                    + "?preprocessors=preprocessing-service-manual&patientIdentifier="
                    + pid
                    + "&lenses="
                    + lens
                )
                print(WEBSITE_URL)
                # WEBSITE_URL = WEBSITE_DATA["url"]
                #  WEBSITE_DESC = WEBSITE_DATA["desc"]
                status_code, warnings = check_website_status(WEBSITE_URL)
                log_result(
                    status_code=status_code,
                    warnings=warnings,
                    method="preprocessperlens",
                    bundleid=bundleid,
                    lens=lens,
                    pid=pid,
                )
    return 1


def chek_all_lenses_data(BUNDLES, PATIENT_IDS, BASE_URL):
    for bundleid in BUNDLES:
        for pid in PATIENT_IDS:
            WEBSITE_URL = (
                BASE_URL
                + "focusing/focus/"
                + bundleid["id"]
                + "?preprocessors=preprocessing-service-manual&patientIdentifier="
                + pid
            )
            print(WEBSITE_URL)
            # WEBSITE_URL = WEBSITE_DATA["url"]
            #  WEBSITE_DESC = WEBSITE_DATA["desc"]
            status_code, warnings = check_website_status(WEBSITE_URL)
            log_result(
                status_code=status_code,
                warnings=warnings,
                method="alllenses",
                bundleid=bundleid,
                lens="all",
                pid=pid,
            )
    return 1


def chek_all_preprocess_data(BUNDLES, PATIENT_IDS, BASE_URL):
    for bundleid in BUNDLES:
        for pid in PATIENT_IDS:
            WEBSITE_URL = (
                BASE_URL
                + "focusing/focus/"
                + bundleid["id"]
                + "?preprocessors=preprocessing-service-mvp2&preprocessors=preprocessing-service-manual&patientIdentifier="
                + pid
            )
            print(WEBSITE_URL)
            # WEBSITE_URL = WEBSITE_DATA["url"]
            #  WEBSITE_DESC = WEBSITE_DATA["desc"]
            status_code, warnings = check_website_status(WEBSITE_URL)
            log_result(
                status_code=status_code,
                warnings=warnings,
                method="allpreprocess",
                bundleid=bundleid,
                lens="all",
                pid=pid,
            )
    return 1


def chek_all_prpcessor_with_post_data(BUNDLES, PATIENT_IDS, BASE_URL):
    for bundleid in BUNDLES:
        bundleresp = requests.get(
            "https://gravitate-health.lst.tfo.upm.es/epi/api/fhir/Bundle/"
            + bundleid["id"]
        )
        bundle = bundleresp.json()
        for pid in PATIENT_IDS:
            patresp = requests.get(
                "https://gravitate-health.lst.tfo.upm.es/ips/api/fhir/Patient/$summary?identifier="
                + pid
            )
            ips = patresp.json()
            #  print(ips)
            body = {"epi": bundle, "ips": ips}
            WEBSITE_URL = (
                BASE_URL
                + "focusing/focus?preprocessors=preprocessing-service-mvp2&preprocessors=preprocessing-service-manual"
            )
            print(WEBSITE_URL)

            # WEBSITE_URL = WEBSITE_DATA["url"]
            #  WEBSITE_DESC = WEBSITE_DATA["desc"]
            status_code, warnings = check_website_status(WEBSITE_URL, body)
            log_result(
                status_code=status_code,
                warnings=warnings,
                method="allpreprocesspost",
                bundleid=bundleid,
                lens="all",
                pid=pid,
            )
    return 1


def check_website_status(url, body=None):
    """
    Checks the status code of a website.
    """
    #  print(body)

    with open("data.json", "w") as json_file:
        json.dump(body, json_file, indent=4)  # indent=4 makes the output more readable

    try:
        if not body:
            response = requests.post(url)
        else:
            # print(body)
            response = requests.post(
                url,
                json=body,
                headers={
                    "content-type": "application/json",
                    "Accept": "application/json",
                },
            )
        # print(response.status_code)
        # print(response.json())
        focusing_warnings = response.headers.get("gh-focusing-warnings")
        # print(focusing_warnings)
        if response.status_code == 400 or focusing_warnings:
            #    print(response.text)
            print(focusing_warnings)
        return response.status_code, focusing_warnings
    except requests.RequestException as e:
        print(f"Error checking website status: {e}")
        return None


def main():
    while True:
        chek_preprocessor_data(BUNDLES, LENSES, PATIENT_IDS, BASE_URL)

        time.sleep(1)

        chek_all_lenses_data(BUNDLES, PATIENT_IDS, BASE_URL)

        time.sleep(1)

        chek_all_preprocess_data(BUNDLES, PATIENT_IDS, BASE_URL)

        time.sleep(1)

        chek_all_prpcessor_with_post_data(BUNDLES, PATIENT_IDS, BASE_URL)


if __name__ == "__main__":
    main()