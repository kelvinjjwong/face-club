A web application help recognize and maintenance faces from images imported by ImageDocker

Target environment: macOS

## Objective of this project:
1. scan picture files from a mounted volume
2. detect and recognize faces from the pictures
3. store the names of recognized faces into database
4. provide front-end to tag and untag faces on pictures

## Major dependencies:
- face detection: dlib, opencv, face_recognition
- web: flask
- db: sqlalchemy(sqlite3), asyncpg
- schedule: apscheduler

## Backend dependency:

- Will connect to PostgreSQL database used by ImageDocker
- Will maintain a SQLite database locally

## Environment setup:

1. Install Anaconda for mac
2. Install Homebrew
3. install following packages by homebrew

```
brew install cmake
brew install xquartz
brew install gtk+3 boost
```

4. initiate a virtual environment by conda

```
cd python_env
./restore_conda_env.sh
```

## Usage

1. Web access

```
http://127.0.0.1:5000
```

2. Command line

- active conda profile

```
conda activate face37
```

'face37' can be customized in python_env/conda_env.conf

- prepare dataset for training

```
/path/to/dataset
/path/to/dataset/person1/picture1.jpg
/path/to/dataset/person1/picture2.jpg
/path/to/dataset/person2/picture1.jpg
/path/to/dataset/person2/picture2.jpg
/path/to/dataset/person3/picture1.jpg
/path/to/dataset/person3/picture2.jpg
```

- train a model

```
python encode_faces.py --dataset /path/to/dataset --encodings model.pickle
```

- recognize faces from a picture

```
python recognize_faces_image.py --encodings model.pickle --image one.jpg --display 0
```
