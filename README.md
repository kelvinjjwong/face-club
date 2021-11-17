Target environment: macOS (I haven't tried other systems.)

## Purpose of this project:
1. scan picture files from a mounted volume
2. detect faces from a set of picture files
3. crop faces and store them to disk and database
4. recognize known (encoded) faces from the cropped faces
5. store the names of recognized faces into database

## Used libraries:
- dlib
- opencv
- face_recognition

Note:

If you would like use Nvidia CUDA, you need an eGPU connected, a macOS High Sierra or lower version, use cmake to build dlib from source by following dlib's instruction.

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
conda env create -f conda_env_python371.yml -n face37
conda activate face37
```
'face37' here is the name of the virtual environment, could be customized.

## Usage

1. train a model

```
python encode_faces.py --dataset dataset --encodings model.pickle
```

2. recognize faces from a picture

```
python recognize_faces_image.py --encodings model.pickle --image one.jpg --display 0
```
