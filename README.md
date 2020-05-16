# Group 10

Welcome on the repository of group 10's assignment for the course Computer Vision. In the sections below you can find instructions on how to setup and run the different assignments in this project.

## Paper
The paper can be found in the directory `paper`. A built version can be found in `main.pdf`.

## Setup

### VS Code
In order to have Python syntax coloring in VS Code for Cython files, add the following entry to your `settings.json`:

```json
"files.associations": {
    "*.pyx": "python"
}
```

#### Prerequisites

This tutorial assumes you have the following dependencies already installed on your pc.
- Python3
- OpenCV
- Numpy

First, install all required Python-packages:

```bash
pip3 install -r requirements.txt
```

Thereafter, start MongoDB. This command will automatically start a Node container to populate the database. Please make sure this container is shut down before you start any Python scripts after task 1.

```bash
docker-compose up --force-recreate
```

If you want to check if the Node container is done with seeding, use the following command. If this commands exits, the seeding is done.

```bash
docker logs -f seed
```

Finally, run the project:

```bash
python src/index.py
```
