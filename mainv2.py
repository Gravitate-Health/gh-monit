import socket
import time
import requests
import os
import json
import logging
from logging.handlers import RotatingFileHandler

# Define the directory and ensure it exists
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
# Set up the logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)  # Configuration


# Configure the rotating file handler
log_file = os.path.join(log_directory, "gh-monit.log")

handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=10)
handler.setLevel(logging.DEBUG)
# Create a formatter and set it for the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


GRAPHITE_HOST = os.getenv(
    "GRAPHITE_HOST", "127.0.0.1"
)  # "host.docker.internal"  # Replace with your Graphite host
GRAPHITE_PORT = os.getenv(
    "GRAPHITE_PORT", 2003
)  # Default port for Carbon plaintext protocol

BASE_URL = os.getenv("BASE_URL", "https://gravitate-health.lst.tfo.upm.es/")
# print(GRAPHITE_HOST, GRAPHITE_PORT)
logger.debug(
    f"BASEURL is {BASE_URL} and HOST IS {GRAPHITE_HOST} and port is  {GRAPHITE_PORT}"
)

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
    logger_method=["graphite"],
    timestamp=None,
    bundleid=None,
    lens=None,
    pid=None,
):
    """
    Sends a metric to Graphite.
    """
    metric_path = f"""gh.focusing.{method}.{bundleid["name"]}.{pid}.{lens}"""
    timestamp = timestamp or int(time.time())
    if status_code == 200 and not warnings:
        value = 0
    elif status_code != 200:
        value = 1
        logger.debug(
            f"Value 1 for {status_code} and method {method} and bundle {bundleid} and pid {pid}"
        )

    elif status_code == 200 and warnings["preprocessingWarnings"]:
        # print(warnings)
        # print(warnings["preprocessingWarnings"])
        value = 2
        logger.debug(
            f"Value 2 for {status_code} and {warnings} and method {method} and bundle {bundleid} and pid {pid}"
        )

    elif status_code == 200 and len(warnings["lensesWarnings"]) > 0:
        value = 3
        logger.debug(
            f"Value 3 for {status_code} and {warnings} and method {method} and bundle {bundleid} and pid {pid}"
        )

    else:
        value = 4
        logger.debug(
            f"Value 4 for {status_code} and {warnings} and method {method} and bundle {bundleid} and pid {pid}"
        )

    message = f"{metric_path} {value} {timestamp}\n"
    # print(f"Sending to Graphite: {message}", end="")

    if "graphite" in logger_method:
        # Open a socket to Graphite and send the data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((GRAPHITE_HOST, int(GRAPHITE_PORT)))
            sock.sendall(message.encode("utf-8"))


# print(LENSES)
PATIENT_IDS = [
    "alicia-1",
    "Cecilia-1",
    "Pedro-1",
    "helen-1",
    "maria-1",
    "0101010101",
    "ips-1",
    "ips-2",
    "ips-3",
    "ips-4",
]
BUNDLES = [
    {
        "id": "bundlepackageleaflet-es-94a96e39cfdcd8b378d12dd4063065f9",
        "name": "biktarvy-es",
    },
    {
        "id": "bundlepackageleaflet-en-94a96e39cfdcd8b378d12dd4063065f9",
        "name": "biktarvy-en",
    },
    {
        "id": "bundlepackageleaflet-es-925dad38f0afbba36223a82b3a766438",
        "name": "calcio-es",
    },
    {
        "id": "bundlepackageleaflet-es-2f37d696067eeb6daf1111cfc3272672",
        "name": "tegretol-es",
    },
    {
        "id": "bundlepackageleaflet-en-2f37d696067eeb6daf1111cfc3272672",
        "name": "tegretol-en",
    },
    {
        "id": "bundlepackageleaflet-es-4fab126d28f65a1084e7b50a23200363",
        "name": "xenical-es",
    },
    {
        "id": "bundlepackageleaflet-en-4fab126d28f65a1084e7b50a23200363",
        "name": "xenical-en",
    },
    {
        "id": "bundlepackageleaflet-es-29436a85dac3ea374adb3fa64cfd2578",
        "name": "hypericum-es",
    },
    {
        "id": "bundlepackageleaflet-es-04c9bd6fb89d38b2d83eced2460c4dc1",
        "name": "flucelvax-es",
    },
    {
        "id": "bundlepackageleaflet-en-04c9bd6fb89d38b2d83eced2460c4dc1",
        "name": "flucelvax-en",
    },
    {
        "id": "bundlepackageleaflet-es-49178f16170ee8a6bc2a4361c1748d5f",
        "name": "dovato-es",
    },
    {
        "id": "bundlepackageleaflet-en-49178f16170ee8a6bc2a4361c1748d5f",
        "name": "dovato-en",
    },
    {
        "id": "bundlepackageleaflet-es-e762a2f54b0b24fca4744b1bb7524a5b",
        "name": "mirtazapine-es",
    },
    {
        "id": "bundlepackageleaflet-es-da0fc2395ce219262dfd4f0c9a9f72e1",
        "name": "blaston-es",
    },
]

PREPROCBUNDLES = [
    {
        "id": "processedbundlekarveabik",
        "name": "biktarvy-en",
    },
    {
        "id": "bundleprocessed-es-b44cce291e466626afa836fffe72c350",
        "name": "biktarvy-es",
    },
    {
        "id": "bundleprocessed-pt-b44cce291e466626afa836fffe72c350",
        "name": "biktarvy-pt",
    },
    {
        "id": "processedbundlekarveacalcium",
        "name": "calcium_pt",
    },
    {
        "id": "processedbundledovato-en",
        "name": "dovato-en",
    },
    {
        "id": "processedbundledovato-es",
        "name": "dovato-es",
    },
    {
        "id": "processedbundleflucelvax",
        "name": "flucelvax-en",
    },
    {
        "id": "processedbundleflucelvaxES",
        "name": "flucelvax-es",
    },
    {
        "id": "processedbundlehypericum",
        "name": "hypericum-es",
    },
    {
        "id": "bundle-ibu-proc",
        "name": "ibuprofen-en",
    },
    {
        "id": "Processedbundlekarvea",
        "name": "karvea-en",
    },
    {
        "id": "bundle-processed-pt-2d49ae46735143c1323423b7aea24165",
        "name": "karvea-pt",
    },
    {
        "id": "bundle-met-proc",
        "name": "metformin-en",
    },
    {
        "id": "bundle-novo-proc",
        "name": "novorapid-en",
    },
    {
        "id": "bundlepackageleaflet-es-proc-2f37d696067eeb6daf1111cfc3272672",
        "name": "tegretrol-es",
    },
    {
        "id": "bundlepackageleaflet-es-proc-4fab126d28f65a1084e7b50a23200363",
        "name": "xenical-es",
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
                time.sleep(1)
    return 1


def chek_lenses_foralreadypreprocess_data(BUNDLES, LENSES, PATIENT_IDS, BASE_URL):
    for bundleid in PREPROCBUNDLES:
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
                    method="send-preprocess",
                    bundleid=bundleid,
                    lens=lens,
                    pid=pid,
                )
                time.sleep(1)

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
            time.sleep(1)

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
            time.sleep(1)

    return 1


def check_bundles_in_list(BASE_URL):
    WEBSITE_URL = BASE_URL + "/Bundle"
    print(WEBSITE_URL)
    response = requests.post(WEBSITE_URL)
    for entry in response.json()["entry"]:
        bid = entry["resource"]["id"]
        nresponse = requests.post(BASE_URL + "/List?item=" + bid)
        if nresponse.json()["total"] > 0:
            value = 0
        else:
            value = 1

        metric_path = f"gh.listmember.{bid}"
        timestamp = int(time.time())

        message = f"{metric_path} {value} {timestamp}\n"
        # print(f"Sending to Graphite: {message}", end="")

        # Open a socket to Graphite and send the data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((GRAPHITE_HOST, int(GRAPHITE_PORT)))
            sock.sendall(message.encode("utf-8"))
    return 1


def chek_all_prpcessor_with_post_data(BUNDLES, PATIENT_IDS, BASE_URL):
    for bundleid in BUNDLES:
        bundleresp = requests.get(BASE_URL + "/Bundle/" + bundleid["id"])
        bundle = bundleresp.json()
        for pid in PATIENT_IDS:
            patresp_body = {
                "resourceType": "Parameters",
                "id": "example",
                "parameter": [
                    {"name": "identifier", "valueIdentifier": {"value": pid}}
                ],
            }
            patresp = requests.post(BASE_URL + "/Patient/$summary", body=patresp_body)
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
            time.sleep(1)

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
        # print(response.text)

        if response.status_code == 400:
            logger.debug(f"Warning: {response.status_code} and {response.text}")
            return response.status_code, {}

        elif focusing_warnings:
            #    print(response.text)
            #    print(focusing_warnings)
            return response.status_code, eval(focusing_warnings)
        else:
            # print(response.status_code)

            return response.status_code, {}
    except requests.RequestException as e:
        print(f"Error checking website status: {e}")
        return None


def main():
    while True:
        try:
            chek_preprocessor_data(BUNDLES, LENSES, PATIENT_IDS, BASE_URL)
        except Exception as err:
            logger.debug(f"Error on function chek_preprocessor_data -> {err}")
        time.sleep(10)
        try:
            chek_all_lenses_data(BUNDLES, PATIENT_IDS, BASE_URL)
        except Exception as err:
            logger.debug(f"Error on function chek_all_lenses_data -> {err}")

        time.sleep(10)
        try:
            chek_all_preprocess_data(BUNDLES, PATIENT_IDS, BASE_URL)
        except Exception as err:
            logger.debug(f"Error on function chek_all_preprocess_data -> {err}")

        time.sleep(10)
        try:
            chek_all_prpcessor_with_post_data(BUNDLES, PATIENT_IDS, BASE_URL)
        except Exception as err:
            logger.debug(
                f"Error on function chek_all_prpcessor_with_post_data -> {err}"
            )

        time.sleep(10)
        try:
            chek_lenses_foralreadypreprocess_data(
                PREPROCBUNDLES, LENSES, PATIENT_IDS, BASE_URL
            )
        except Exception as err:
            logger.debug(
                f"Error on function chek_lenses_foralreadypreprocess_data -> {err}"
            )

        time.sleep(3600)


if __name__ == "__main__":
    main()
