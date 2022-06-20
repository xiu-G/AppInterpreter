
import numpy as np
import os, errno
import cv2
import argparse
import sys
np.set_printoptions(threshold=sys.maxsize)

def convert_transparent(image_original, factor_background):
	alpha_channel = image_original[:,:,3]
	rgb_channels = image_original[:,:,:3]

	# White Background Image
	white_background_image = np.ones_like(rgb_channels, dtype=np.uint8) * factor_background

	# Alpha factor
	alpha_factor = alpha_channel[:,:,np.newaxis].astype(np.float32) / 255.0
	alpha_factor = np.concatenate((alpha_factor,alpha_factor,alpha_factor), axis=2)

	# Transparent Image Rendered on White Background
	base = rgb_channels.astype(np.float32) * alpha_factor
	white = white_background_image.astype(np.float32) * (1 - alpha_factor)
	final_image = base + white
	return final_image

def read_transparent_png(image_original):
	if len(image_original.shape) == 2:
		return image_original

	height, width, channel = image_original.shape

	if channel == 3:
		return image_original
	

	final_white_background_image = convert_transparent(image_original, 255.0)

	b_channel = final_white_background_image[:,:,0]
	g_channel = final_white_background_image[:,:,1]
	r_channel = final_white_background_image[:,:,2]

	sum_b = np.sum(b_channel)/(height*width)
	sum_g = np.sum(g_channel)/(height*width)
	sum_r = np.sum(r_channel)/(height*width)

	if sum_b == sum_g and sum_g == sum_r and sum_r <= 255.0 and sum_r >= 250.0:
		return convert_transparent(image_original, 0)

	return final_white_background_image

def resize_image(output_dir, imagePath):	
	# print(imagePath)
	image_original = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
	try:
		height, width, channel = image_original.shape
	except:
		return
	ratio = width/height

	if ratio >= 0.5 and ratio <= 2:
		image = read_transparent_png(image_original)

		# perform the actual resizing of the image and show it
		resized = cv2.resize(image, (128,128), interpolation = cv2.INTER_AREA)

		cv2.imwrite(os.path.join(output_dir, os.path.basename(imagePath)), resized)
    
def main(out_path, input_file):
	# parser = argparse.ArgumentParser(description="Resize the icons.", formatter_class=argparse.RawTextHelpFormatter)
	# parser.add_argument("-i", action="store", dest="input_file", required=True, help="The input")
	# parser.add_argument("-o", action="store", dest="output_dir", required=True, help="The output dir")
	# options = parser.parse_args()

	resize_image(out_path, input_file)

if __name__ == '__main__':
    out_put = ''
    input_file = '/home/data/xiu/code-translation/code/DeepIntent/data/decode_dir/com.MyPersonalDiarywithLockFingerprintPassword_7/res/drawable/cancel.png'
    main(out_put, input_file)
