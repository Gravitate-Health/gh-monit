import json
import logging
import os
import socket
import threading
import time
from logging.handlers import RotatingFileHandler

from requests_futures.sessions import FuturesSession
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

metrics = {}

import requests

from dotenv import load_dotenv

load_dotenv()

# Enabled metrics API
ENABLE_METRICS_API = os.getenv("ENABLE_METRICS_API", False)
if (ENABLE_METRICS_API == "True"): ENABLE_METRICS_API = True
if (ENABLE_METRICS_API == "False"): ENABLE_METRICS_API = False
if (ENABLE_METRICS_API == True):
    from flask import Flask, Response
    app = Flask(__name__)

# Define the directory and ensure it exists
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
# Set up the logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Configuration

# Enable logging to the console for all modules
logging.basicConfig(level=logging.INFO)


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
    "GRAPHITE_HOST", None
)  # "host.docker.internal"  # Replace with your Graphite host
GRAPHITE_PORT = os.getenv(
    "GRAPHITE_PORT", 2003
)  # Default port for Carbon plaintext protocol

BASE_URL = os.getenv("BASE_URL", "https://gravitate-health.lst.tfo.upm.es/")
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", None)
# print(GRAPHITE_HOST, GRAPHITE_PORT)

logger_methods = []
if PUSHGATEWAY_URL != None: logger_methods.append("prometheus")
if GRAPHITE_HOST != None: logger_methods.append("graphite")

print("ENABLE_METRICS_API", ENABLE_METRICS_API)
print("PUSHGATEWAY_URL", PUSHGATEWAY_URL)
print("GRAPHITE_HOST", GRAPHITE_HOST)
print("GRAPHITE_PORT", GRAPHITE_PORT)
print("BASE_URL", BASE_URL)
print("logger_methods", logger_methods)

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
    logger_method=logger_methods,
    timestamp=None,
    bundleid=None,
    lens=None,
    pid=None,
):
    """
    Logs a metric to be exposed for Prometheus or Graphite.
    """
    metric_path = f"""gh_focusing_{method}_{bundleid["name"]}_{pid}_{lens}"""
    timestamp = timestamp or int(time.time())
    metric_path = metric_path.replace("-", "_")
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

    metrics[metric_path] = value

    if "prometheus" in logger_method:
        registry = CollectorRegistry()
        g = Gauge(metric_path, 'Description of gauge', registry=registry)
        g.set(value)
        push_to_gateway(PUSHGATEWAY_URL, job='gh_monit', registry=registry)
    if "graphite" in logger_method:
        message = f"{metric_path} {value} {timestamp}\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((GRAPHITE_HOST, int(GRAPHITE_PORT)))
            sock.sendall(message.encode("utf-8"))
    if "file" in logger_method:
        message = f"{metric_path} {value} {timestamp}\n"
        print(f"Sending to Graphite: {message}", end="")


if ENABLE_METRICS_API == True:
    @app.route("/metrics")
    def metrics_endpoint():
        metrics_data = "\n".join([f"{key} {value}" for key, value in metrics.items()])
        print(metrics_data)
        return Response(metrics_data, mimetype="text/plain")


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


def prepare_requests(BUNDLES, LENSES, PATIENT_IDS, BASE_URL, method):
    session = FuturesSession()
    requests_list = []

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
                requests_list.append(
                    (session.post(WEBSITE_URL), bundleid, lens, pid, method)
                )

    return requests_list


def process_responses(requests_list):
    for future, bundleid, lens, pid, method in requests_list:
        response = future.result()
        status_code, warnings = check_website_status(response)
        log_result(
            status_code=status_code,
            warnings=warnings,
            method=method,
            bundleid=bundleid,
            lens=lens,
            pid=pid,
        )


def check_website_status(response):
    """
    Checks the status code of a website.
    """
    focusing_warnings = response.headers.get("gh-focusing-warnings")

    if response.status_code == 400:
        logger.debug(f"Warning: {response.status_code} and {response.text}")
        return response.status_code, {}

    elif focusing_warnings:
        return response.status_code, eval(focusing_warnings)
    else:
        return response.status_code, {}


def check_bundles_in_list(BASE_URL):
    ENCHACED_WHITE_LIST = [
        "enhanced-bundlebik-alicia",
        "enhanced-bundlekarveacalcium-alicia",
        "enchanced-bundledovato-es",
        "enchanced-bundledovato-en",
        "enhanced-bundleflucelvax-alicia",
        "enhanced-bundlehypericum-alicia",
        "enhancedbundlekarvea-alicia",
        "enhancedddbundlekarvea",
        "enhanced-bundlebik-pedro",
        "enhanced-bundlekarveacalcium-pedro",
        "enchanced-bundledovato-pedro-en",
        "enchanced-bundledovato-pedro-es",
        "enhanced-bundleflucelvax-pedro",
        "enhanced-bundlehypericum-pedro",
        "enhancedbundlekarveaP",
    ]
    WEBSITE_URL = BASE_URL + "epi/api/fhir/Bundle"
    print(WEBSITE_URL)

    next_url = WEBSITE_URL  # Start with the initial URL

    while next_url:  # Loop through bundles while 'next' link exists
        response = requests.get(next_url)

        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break

        # Parse the JSON response
        data = response.json()

        # Process entries in the current bundle
        if "entry" in data:
            for entry in data["entry"]:
                bid = entry["resource"]["id"]
                if bid in ENCHACED_WHITE_LIST:
                    continue
                print(f"Processing bundle ID: {bid}")

                # Check the 'List' resource for the current bundle ID
                nresponse = requests.get(f"{BASE_URL}epi/api/fhir/List?item={bid}")

                if nresponse.status_code != 200:
                    print(f"Failed to check List resource: {nresponse.status_code}")
                    continue

                if nresponse.json().get("total", 0) > 0:
                    value = 0  # If the resource is found
                else:
                    value = 1  # If the resource is not found

                metric_path = f"gh.listmember.{bid}"
                timestamp = int(time.time())

                message = f"{metric_path} {value} {timestamp}\n"
                # print(f"Sending to Graphite: {message}", end="")
                print(message)

                # Open a socket to Graphite and send the data
                # Uncomment and modify if sending to Graphite
                # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                #     sock.connect((GRAPHITE_HOST, int(GRAPHITE_PORT)))
                #     sock.sendall(message.encode("utf-8"))

        # Check for the next link to paginate
        next_url = None
        for link in data.get("link", []):
            if link["relation"] == "next":
                next_url = link["url"]
                print(f"Fetching next page: {next_url}")
                break  # We only need the first 'next' link
    print("end")
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
    return 1


def log_result_preproc(
    method,
    logger_method=["prometheus"],
    timestamp=None,
    bundleid=None,
    language=None,
    extension_count=0,
    applied_extension_count=0,
):
    """
    Sends a metric to Prometheus PushGateway or Graphite.
    """
    if "prometheus" in logger_method:
        metric_path = f"""gh_preproc_{method}_{bundleid}_{language}"""
    else:
        metric_path = f"""gh.preproc.{method}.{bundleid}.{language}"""
    timestamp = timestamp or int(time.time())
    if extension_count == 0:
        value = 1
    elif applied_extension_count == 0:
        value = 1
    else:
        value = 0

    if "prometheus" in logger_method:
        registry = CollectorRegistry()
        g = Gauge(metric_path, 'Description of gauge', registry=registry)
        g.set(value)
        push_to_gateway(PUSHGATEWAY_URL, job='gh_monit', registry=registry)
    elif "graphite" in logger_method:
        message = f"{metric_path} {value} {timestamp}\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((GRAPHITE_HOST, int(GRAPHITE_PORT)))
            sock.sendall(message.encode("utf-8"))
    elif "file" in logger_method:
        message = f"{metric_path} {value} {timestamp}\n"
        print(f"Sending to Graphite: {message}", end="")


def test_preprocessor(BASEURL, epiid, language):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    url = (
        BASEURL
        + "/focusing/preprocessing/"
        + epiid
        + "?preprocessors=preprocessing-service-mvp2"
    )

    response = requests.post(url, headers=headers)
    # print(response.text)
    result = response.json()

    composition = result["entry"][0]
    ##  print(composition)
    json_string = json.dumps(composition)

    extension_count = json_string.count(
        "https://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink"
    )
    # print(extension_exist)  # Output: ?
    # print(word_in_json(composition, "composition"))  # Output: True
    # print(word_in_json(composition, "whites"))  # Output: True
    if extension_count == 0:
        print(epiid, "No extension")
    # file.write(epiid + ", No extension\n")
    elif extension_count > 0:
        print(epiid, "Has extension")

    # file.write(epiid + ", " + str(extension_count) + "\n")
    log_result_preproc(
        method="preprocessing-service-mvp2",
        language=language,
        bundleid=epiid,
        extension_count=extension_count,
    )

    return 1


def fetch_paginated_data(BASEURL):
    """
    Makes a GET request to a URL, checks for a 'next' element in the response,
    and continues fetching data while 'next' exists.

    Args:
        BASEURL (str): The base URL to fetch data from.
    """
    url = f"{BASEURL}epi/api/fhir/Bundle"

    while url:
        print(f"Fetching data from: {url}")

        # Make a GET request
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
        except requests.RequestException as e:
            print(f"Failed to fetch data: {e}")
            break

        # Parse the JSON response
        data = response.json()
        if "entry" not in data:
            print("No 'entry' found in the response. Skipping this page.")
            break

        # Process each entry in the current bundle
        for entry in data["entry"]:
            bundle = entry.get("resource", {})
            composition = bundle.get("entry", [{}])[0].get("resource", {})
            id_ = bundle.get("id")
            if not id_:
                continue  # Skip if no ID is found

            language = composition.get("language")
            if not language or language in ["no", "fi", "ja"]:
                continue

            category = composition.get("category")
            if category is None:
                test_preprocessor(BASEURL, id_, language)
            elif category[0]["coding"][0]["code"] == "R":
                test_preprocessor(BASEURL, id_, language)

        # Check for the 'next' key in the response
        next_url = None
        for link in data.get("link", []):
            if link.get("relation") == "next":
                next_url = link.get("url")
                break

        # Update the URL or exit if no 'next' link is found
        if not next_url or url == next_url:
            print("No more pages. Finished processing.")
            break
        else:
            url = next_url


def main():
    # Run the Flask app in a separate thread
    if ENABLE_METRICS_API == True:
        threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()

    while True:
        try:
            requests_list = prepare_requests(
                BUNDLES, LENSES, PATIENT_IDS, BASE_URL, "preprocessperlens"
            )
            process_responses(requests_list)
        except Exception as err:
            logger.debug(f"Error on function chek_preprocessor_data -> {err}")

        try:
            requests_list = prepare_requests(
                BUNDLES, ["all"], PATIENT_IDS, BASE_URL, "alllenses"
            )
            process_responses(requests_list)
        except Exception as err:
            logger.debug(f"Error on function chek_all_lenses_data -> {err}")

        try:
            requests_list = prepare_requests(
                BUNDLES, ["all"], PATIENT_IDS, BASE_URL, "allpreprocess"
            )
            process_responses(requests_list)
        except Exception as err:
            logger.debug(f"Error on function chek_all_preprocess_data -> {err}")

        try:
            requests_list = prepare_requests(
                PREPROCBUNDLES, LENSES, PATIENT_IDS, BASE_URL, "send-preprocess"
            )
            process_responses(requests_list)
        except Exception as err:
            logger.debug(
                f"Error on function chek_lenses_foralreadypreprocess_data -> {err}"
            )

        try:
            check_bundles_in_list(BASE_URL)
        except Exception as err:
            logger.debug(f"Error on function check_bundles_in_list -> {err}")

        try:
            fetch_paginated_data(BASE_URL)
        except Exception as err:
            logger.debug(f"Error on function check_bundles_in_list -> {err}")

        time.sleep(3600)


if __name__ == "__main__":
    main()
