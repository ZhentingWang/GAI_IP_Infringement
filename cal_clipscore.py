import glob
import os
from diffusers import StableDiffusionPipeline,StableDiffusionXLPipeline,AutoPipelineForText2Image,VQDiffusionPipeline
import torch
#from scheduler_dev import DDIMSchedulerDev
from torchmetrics.functional.multimodal import clip_score
from functools import partial
import torchvision.transforms as transforms 
import numpy as np
import argparse
from PIL import Image

def get_image_paths(folder):
    image_formats = ["*.jpg", "*.jpeg", "*.png"]
    image_paths = []
    for image_format in image_formats:
        image_paths.extend(glob.glob(os.path.join(folder, image_format)))
    return image_paths
def calculate_clip_score(images, prompts):
    images_int = (images * 255).astype("uint8")
    clip_score = clip_score_fn(torch.from_numpy(images_int).permute(0, 3, 1, 2), prompts).detach()
    return round(float(clip_score), 4)

parser = argparse.ArgumentParser(description='')
parser.add_argument('--images_dir_name', type=str, default=None)
parser.add_argument('--prompt_file_name', type=str, default=None)

args = parser.parse_args()

with open(args.prompt_file_name, 'r') as f:
    lines = f.readlines()
prompt_list = []
for line in lines:
    prompt_list.append(line.strip())

folder_path = args.images_dir_name
image_path_list = get_image_paths(folder_path)

assert len(prompt_list) == len(image_path_list)

total = 0
for i in range(len(prompt_list)):
    #print("*"*100)
    #print(i)
    image = Image.open(image_path_list[i])
    prompt = prompt_list[i]
    clip_score_fn = partial(clip_score, model_name_or_path="openai/clip-vit-base-patch16")
    clip_score_calculated = calculate_clip_score(np.expand_dims(np.array(image), axis=0), [prompt])
    print(f"CLIP score: {clip_score_calculated}")
    total = total + clip_score_calculated

print("avg clip_score: ", total/len(prompt_list))
