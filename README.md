# Group 10

Welcome on the repository of group 10's assignment for the course Computer Vision. In the sections below you can find instructions on how to setup and run the different assignments in this project.

## Setup

#### Prerequisites

This tutorial assumes you have the following dependencies already installed on your pc.
- Python3
- OpenCV
- Numpy

First, install all required Python-packages.

```bash
pip3 install -r requirements.txt
```

Thereafter, start MongoDB. If you want to seed the database, unzip the file `db-seed/dump.zip` before running the next command and run the first command. If you don't want to seed the database, please add `mongodb` after the `-d` option of the next command (see second command).

```bash
# WITH SEED
# This command will automatically start a Node container to populate the database.
# Please make sure this container is shut down before you start any Python scripts after task 1.
docker-compose up --force-recreate -d

# WITHOUT SEED
docker-compose up --force-recreate -d mongodb
```

Finally, run the project.

```bash
python src/index.py
```
