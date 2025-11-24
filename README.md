# Speaking-museum
Based on the concept of [Speaking Images](https://github.com/VBernasconi/Speaking-Images), this repository proposes a simplified version of a speaking image generator without LLMs. It has to be used with a set of images and their corresponding texts in a separate folder (see 'SETUP PROJECT STRUCTURE' bellow). The script will generated short videos where characters represented in the images will recite the given text. This repository is intended to help the generation of multiple speaking images in a curatorial context. Additionaly, it proposes the integration of output videos into a simple AR application using [MindAR](https://hiukim.github.io/mind-ar-js-doc/)

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
python speaking_art.py --image_folder $image_folder --desc $description_folder
```
## HOW TO CITE
```
@software{speaking_images,
  author = {Valentine Bernasconi},
  title = {Speaking Images},
  year = {2025},
  url = {https://github.com/VBernasconi/Speaking-Images},
  doi = {10.5281/zenodo.17701405}
}
```
```
@inproceedings{11204281,
  author={Bernasconi, Valentine and Marfia, Gustavo},
  booktitle={2025 IEEE 35th International Workshop on Machine Learning for Signal Processing (MLSP)}, 
  title={Speaking Images. A Novel Framework for the Automated Self-Description of Artworks}, 
  year={2025},
  volume={},
  number={},
  pages={1-6},
  doi={10.1109/MLSP62443.2025.11204281}}
```
