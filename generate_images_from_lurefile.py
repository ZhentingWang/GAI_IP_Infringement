
import os
from diffusers import StableDiffusionPipeline,StableDiffusionXLPipeline,AutoPipelineForText2Image,VQDiffusionPipeline
import torch
import argparse
from openai import OpenAI
import requests

parser = argparse.ArgumentParser(description='')
parser.add_argument('--arch', type=str, default='')
parser.add_argument('--char', type=str, default=None)
parser.add_argument('--prompt_file_name', type=str, default=None)
parser.add_argument('--negative_prompt', type=str, default=None)

args = parser.parse_args()


if args.arch in ["sdxl","sdxl512"]:
    cur_model = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float32
    )
    cur_model = cur_model.to("cuda")
    cur_model.unet.eval()
    cur_model.vae.eval()
elif args.arch=="sd":
    model_id = "runwayml/stable-diffusion-v1-5"
    cur_model = StableDiffusionPipeline.from_pretrained(model_id,torch_dtype=torch.float32).to("cuda")
    cur_model.unet.eval()
    cur_model.vae.eval()
elif args.arch=="sdv2base":
    model_id = "stabilityai/stable-diffusion-2-base"
    cur_model = StableDiffusionPipeline.from_pretrained(model_id,torch_dtype=torch.float32).to("cuda")
    cur_model.unet.eval()
    cur_model.vae.eval()
elif args.arch=="sdv21":
    model_id = "stabilityai/stable-diffusion-2-1"
    cur_model = StableDiffusionPipeline.from_pretrained(model_id,torch_dtype=torch.float32).to("cuda")
    cur_model.unet.eval()
    cur_model.vae.eval()
elif args.arch=="kandinsky":
    cur_model = AutoPipelineForText2Image.from_pretrained(
                        "kandinsky-community/kandinsky-2-1", torch_dtype=torch.float32
                    )
    cur_model = cur_model.to("cuda")
elif args.arch=="vqdiffusion":
    cur_model = VQDiffusionPipeline.from_pretrained("microsoft/vq-diffusion-ithq", torch_dtype=torch.float32)
    cur_model = cur_model.to("cuda")
elif args.arch=="sdxlturbo":
    cur_model = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float32, variant="fp32")
    cur_model.to("cuda")
    cur_model.unet.to("cuda")
    cur_model.vae.to("cuda")
    cur_model.unet.eval()
    cur_model.vae.eval()

if args.arch=="sdxlturbo":
    inference_steps = 1
    guidance_scale = 0.0
else:
    inference_steps = 50
    guidance_scale=7.5

save_folder = "./"+args.char+"_"+args.arch+"_generated_imgs/"

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

with open(args.prompt_file_name, 'r') as f:
    lines = f.readlines()

prompt_list = []
for line in lines:
    prompt_list.append(line.strip())

print(prompt_list)

if args.arch=="dalle3api":
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    counter = 0
    prompt_list = prompt_list[:20]
    for prompt in prompt_list:
        for i in range(1):
            try:
                response = client.images.generate(
                model="dall-e-3",
                prompt="generate an image: "+prompt,
                size="1024x1024",
                quality="standard",
                n=1,
                )
                path = save_folder+"prompt"+str(counter)+"_"+str(i)+".png"

                image_data = response.data[0].url
                
                image_response = requests.get(image_data)
                
                with open(path, 'wb') as file:
                    file.write(image_response.content)
                print("Image saved successfully.")
            except:
                print("Image is blocked.")

        counter = counter + 1
else:
    counter = 0
    for prompt in prompt_list:
        for i in range(1):
            if args.arch=="sdxl512":
                image = cur_model(prompt, negative_prompt = args.negative_prompt, height=512, width=512, num_inference_steps=inference_steps, guidance_scale=guidance_scale,output_type="pil",return_dict=False)
            else:
                image = cur_model(prompt, negative_prompt = args.negative_prompt, num_inference_steps=inference_steps, guidance_scale=guidance_scale,output_type="pil",return_dict=False)
            image = image[0][0]
            path = save_folder+"prompt"+str(counter)+"_"+str(i)+".png"
            image.save(path)
        counter = counter + 1