
# GH-MONIT

![Latest release](https://img.shields.io/github/v/release/Gravitate-Health/gh-monit)
![Actions workflow](https://github.com/Gravitate-Health/gh-monit/actions/workflows/cicd.yml/badge.svg)
![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![License](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache)


## Table of contents

- [GH-MONIT](#gh-monit)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Deployment](#deployment)
      - [Kubernetes (Kustomize)](#kubernetes-kustomize)
  - [Usage](#usage)
  - [Known issues and limitations](#known-issues-and-limitations)
  - [Getting help](#getting-help)
  - [Contributing](#contributing)
  - [Authors and history](#authors-and-history)
  - [Acknowledgments](#acknowledgments)


## Introduction

This repository includes an implementation of a monitor for Gravitate Health resources. It publishes metrics regarding the status of ePIs, preprocessors, and focusing status.

## Deployment

#### Kubernetes (Kustomize)

Production: 
```bash
kubectl apply -k kubernetes/base
```

Development: 
```bash
kubectl apply -k kubernetes/dev
```


Usage
-----

Known issues and limitations
----------------------------

Getting help
------------
In case you find a problem or you need extra help, please use the issues tab to report the issue.

Contributing
------------
To contribute, fork this repository and send a pull request with the changes squashed.

Authors and history
---------------------------
- João Almeida ([@joofio](https://github.com/joofio))
- Guillermo Mejías ([@gmej](https://github.com/gmej))

Acknowledgments
---------------------------
- [ORIGINAL DEVELOPMENT by @joofio](https://github.com/joofio/gh-monit)