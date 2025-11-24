# Speaking-museum
Based on the concept of [Speaking Images](https://github.com/VBernasconi/Speaking-Images), this repository proposes a simplified version without the use of an LLM. It has to be used with a set of images and their corresponding descriptions in a separate folder.

## DOWNLOAD THE FOLLOWING OPEN SOURCE LIBRARIES
- [DeepFace](https://github.com/serengil/deepface)
- [Kokoro-tts](https://github.com/hexgrad/kokoro)
- [hallo](https://github.com/fudan-generative-vision/hallo/)

## SETUP A CONDA ENVIRONMENT
First create a conda environment
```
conda create -n speaking_museum_venv python=3.10
conda activate speaking_museum_venv
```
## INSTALL REQUIREMENTS
```
pip install requirements.txt
```
## SETUP PROJECT STRUCTURE
Make sure you include your images in an image folder
```
.
├── hallo                   
├── kokoro
├── descriptions
│   ├── img_00.txt       
│   ├── img_01.txt    
│   └── ...                                      
├── images
│   ├── img_00.jpeg        
│   ├── img_01.jpeg    
│   └── ...
├── requirements.txt                    
├── speaking_art.py                   
└── README.md
```
Then run the following command

```
python speaking_art.py --image_folder $image_folder --desc $description_fodler
```
