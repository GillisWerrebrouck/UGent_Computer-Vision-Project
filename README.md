# Group 10

Welcome on the repository of group 10's assignment for the course Computer Vision. In the sections below you can find instructions on how to setup and run the different assignments in this project.

## Setup

#### Prerequisites

This tutorial assumes you have the following dependencies already installed on your pc.
- Python3
- OpenCV
- Numpy

First, install all required Python-packages:

```bash
pip3 install -r requirements.txt
```

Thereafter, start MongoDB:

```bash
docker-compose up --force-recreate -d mongodb
```

Finally, run the project:

(TODO: add ability to choose between different assignments)
```bash
python src/index.py
```
