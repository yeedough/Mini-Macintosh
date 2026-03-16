import cv2
from PIL import Image
import os
import sys
import numpy as np

# --- Settings ---
INPUT_FILE = 'input.mp4'
OUTPUT_FILE = 'video.bin'
WIDTH = 128
HEIGHT = 64
TARGET_FPS = 30  # target video fps

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: '{INPUT_FILE}' not found!")
        return

    cap = cv2.VideoCapture(INPUT_FILE)
    
    # Getting the input video fps
    source_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Source Video FPS: {source_fps}")
    TARGET_FPS = int(input("Enter the desired fps value (Try to keep it below 30)\nTARGET_FPS = "))

    # Frame skip calculator
    frame_skip = 1
    if source_fps > TARGET_FPS:
        frame_skip = int(source_fps / TARGET_FPS)

    output_data = bytearray()

    # --- NEW: FPS value ---
    output_data.append(int(TARGET_FPS))
    print(f"Header added: FPS value ({TARGET_FPS}) written to the beginning of the file.")
    # -------------------------------------------
    
    processed_frames = 0
    current_frame = 0

    selection = int(input("For monochrome videos choose 0, for colorful videos choose one of the rest; \n1: Floyd-Steinberg\n2: No dithering (Pure treshold) \n3: No dithering in convert \n4: Ordered Dithering (Bayer matrix) \nYour choice: "))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if current_frame % frame_skip != 0:
            current_frame += 1
            continue

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)
        im_pil = im_pil.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

        # Thresholding (Bad Apple or colorful)
        if selection == 0:  
            thresh = 128
            fn = lambda x: 255 if x > thresh else 0
            im_pil = im_pil.convert('L').point(fn, mode='1') #monochrome

        elif selection == 1:
            im_pil = im_pil.convert('1') #Floyd-Steinberg (your current behavior, explicitly)

        elif selection == 2: #No dithering at all (pure threshold)
            im_pil = im_pil.convert('L')  
            im_pil = im_pil.point(lambda x: 255 if x > 128 else 0, '1')

        elif selection == 3: #Disable dithering in convert()
            im_pil = im_pil.convert('L').convert('1', dither=Image.Dither.NONE)

        elif selection == 4: #Ordered dithering (Bayer matrix)
            bayer_4x4 = np.array([
            [ 0, 128,  32, 160],
            [192,  64, 224,  96],
            [ 48, 176,  16, 144],
            [240, 112, 208,  80]
            ], dtype=np.uint8)

            gray = np.array(im_pil.convert('L'))
            tiled = np.tile(bayer_4x4, (gray.shape[0] // 4 + 1, gray.shape[1] // 4 + 1))[:gray.shape[0], :gray.shape[1]]
            bayer_result = (gray > tiled).astype(np.uint8) * 255
            im_pil = Image.fromarray(bayer_result).convert('1')
            
        pixels = im_pil.load()
        frame_bytes = bytearray()
        
        # Vertical Packing (OLED Page Format)
        for page in range(8):
            for x in range(128):
                byte_val = 0
                for bit in range(8):
                    y = page * 8 + bit
                    if pixels[x, y] > 0:
                        byte_val |= (1 << bit)
                frame_bytes.append(byte_val)
        
        output_data.extend(frame_bytes)
        processed_frames += 1
        current_frame += 1

        sys.stdout.write(f"\rFrame: {processed_frames} | Size: {len(output_data)/1024:.1f} KB")
        sys.stdout.flush()

    cap.release()
    
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(output_data)

    print(f"\n\n--- DONE ---")
    print("Video FPS value has been added to the file.")

if __name__ == "__main__":
    main()
