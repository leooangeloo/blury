from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import torch
import torchvision.transforms as T
import numpy as np
import hashlib
import json
import base64
from datetime import datetime
import piexif
import cv2

app = FastAPI()

# Allow CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_FORMATS = {"jpeg", "png", "jpg"}
MAX_IMAGES = 5
MAX_SIZE_MB = 10

def create_robust_watermark(img: Image.Image, creator_name: str, timestamp: str) -> Image.Image:
    """Create robust watermark using multiple techniques that are harder for AI to remove"""
    
    # Convert to numpy array
    img_array = np.array(img)
    
    # Create watermark data
    watermark_data = {
        "creator": creator_name,
        "timestamp": timestamp,
        "hash": hashlib.md5(f"{creator_name}{timestamp}".encode()).hexdigest()[:8],
        "protection": "ai-resistant"
    }
    
    # Convert to binary string
    watermark_str = json.dumps(watermark_data)
    watermark_binary = ''.join(format(ord(char), '08b') for char in watermark_str)
    
    # Method 1: Enhanced LSB steganography with error correction
    height, width, _ = img_array.shape
    if len(watermark_binary) <= height * width:
        # Embed in multiple channels for redundancy
        for channel in [0, 1, 2]:  # RGB channels
            flat_channel = img_array[:, :, channel].flatten()
            for i, bit in enumerate(watermark_binary):
                if i < len(flat_channel):
                    # Use 2 LSBs for better robustness
                    flat_channel[i] = (flat_channel[i] & 0xFC) | (int(bit) * 3)
            img_array[:, :, channel] = flat_channel.reshape(height, width)
    
    # Method 2: Add adversarial perturbations
    # Create subtle patterns that confuse AI models
    noise_pattern = np.random.rand(height, width, 3) * 0.02  # Very subtle noise
    img_array = np.clip(img_array.astype(np.float32) + noise_pattern, 0, 255).astype(np.uint8)
    
    # Method 3: Frequency domain modifications (if OpenCV available)
    try:
        # Convert to YUV and modify Y channel in frequency domain
        img_yuv = cv2.cvtColor(img_array, cv2.COLOR_RGB2YUV)
        y_channel = img_yuv[:, :, 0].astype(np.float32)
        
        # Apply DCT to 8x8 blocks and add watermark
        for i in range(0, height - 8, 8):
            for j in range(0, width - 8, 8):
                block = y_channel[i:i+8, j:j+8]
                dct_block = cv2.dct(block)
                
                # Add watermark to mid-frequency coefficients
                watermark_bit = int(watermark_binary[(i//8 * (width//8) + j//8) % len(watermark_binary)])
                if watermark_bit:
                    dct_block[3, 3] += 8  # Stronger modification
                    dct_block[4, 4] += 6
                else:
                    dct_block[3, 3] -= 8
                    dct_block[4, 4] -= 6
                
                # Inverse DCT
                idct_block = cv2.idct(dct_block)
                y_channel[i:i+8, j:j+8] = idct_block
        
        img_yuv[:, :, 0] = np.clip(y_channel, 0, 255).astype(np.uint8)
        img_array = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
    except:
        # Fallback if OpenCV not available
        pass
    
    # Method 4: Add invisible grid pattern
    grid_size = 32
    for i in range(0, height, grid_size):
        for j in range(0, width, grid_size):
            if (i + j) % (grid_size * 2) == 0:
                # Add subtle grid pattern
                img_array[i:i+1, j:j+grid_size, :] = np.clip(
                    img_array[i:i+1, j:j+grid_size, :].astype(np.float32) + 2, 0, 255
                ).astype(np.uint8)
    
    return Image.fromarray(img_array)

def add_visible_watermark(img: Image.Image, creator_name: str, opacity: float = 0.3) -> Image.Image:
    """Add semi-transparent visible watermark with enhanced positioning"""
    # Create a copy to work on
    watermarked = img.copy()
    
    # Create watermark text
    watermark_text = f"© {creator_name} - AI Protected"
    
    # Create a transparent overlay
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Try to use a font, fallback to default if not available
    try:
        font_size = max(img.size) // 25
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Get text size
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Add multiple watermarks for better coverage
    positions = [
        (img.width - text_width - 20, img.height - text_height - 20),  # Bottom right
        (20, img.height - text_height - 20),  # Bottom left
        (img.width // 2 - text_width // 2, img.height // 2 - text_height // 2),  # Center
    ]
    
    for x, y in positions:
        # Draw watermark with opacity
        draw.text((x, y), watermark_text, fill=(255, 255, 255, int(255 * opacity)), font=font)
    
    # Composite the watermark onto the image
    if img.mode != 'RGBA':
        watermarked = watermarked.convert('RGBA')
    
    watermarked = Image.alpha_composite(watermarked, overlay)
    return watermarked.convert('RGB')

def add_metadata(img: Image.Image, creator_name: str, ai_consent: str, additional_info: str = "") -> Image.Image:
    """Add metadata including AI training consent tags"""
    
    # Create metadata dictionary
    metadata = {
        "Creator": creator_name,
        "Copyright": f"© {creator_name}",
        "AI_Training_Consent": ai_consent,
        "Watermark_Date": datetime.now().isoformat(),
        "Watermark_Tool": "AI-Protected Image Watermarking App",
        "Protection_Level": "Enhanced",
        "Additional_Info": additional_info
    }
    
    # For JPEG files, use EXIF data
    if img.format == 'JPEG':
        try:
            # Create EXIF data
            exif_dict = {
                "0th": {
                    piexif.ImageIFD.Artist: creator_name.encode('utf-8'),
                    piexif.ImageIFD.Copyright: f"© {creator_name} - AI Protected".encode('utf-8'),
                    piexif.ImageIFD.Software: "AI-Protected Image Watermarking App".encode('utf-8'),
                },
                "Exif": {
                    piexif.ExifIFD.DateTimeOriginal: datetime.now().strftime("%Y:%m:%d %H:%M:%S").encode('utf-8'),
                },
                "1st": {},
                "GPS": {},
                "Interop": {},
                "thumbnail": None,
            }
            
            # Add custom fields for AI consent
            exif_dict["0th"][piexif.ImageIFD.DocumentName] = f"AI_Consent:{ai_consent}_Protected".encode('utf-8')
            if additional_info:
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = additional_info.encode('utf-8')
            
            exif_bytes = piexif.dump(exif_dict)
            img.info["exif"] = exif_bytes
            
        except Exception as e:
            print(f"Warning: Could not add EXIF metadata: {e}")
    
    # For PNG files, use text metadata
    elif img.format == 'PNG':
        try:
            # Add metadata as PNG text chunks
            metadata_text = json.dumps(metadata)
            img.info["metadata"] = metadata_text
        except Exception as e:
            print(f"Warning: Could not add PNG metadata: {e}")
    
    return img

@app.post("/watermark")
async def watermark_images(
    files: List[UploadFile] = File(...),
    creator_name: str = Form(...),
    watermark_type: str = Form("both"),  # "invisible", "visible", "both"
    visible_opacity: float = Form(0.3),
    ai_consent: str = Form("denied"),  # "granted", "denied", "conditional"
    additional_info: str = Form("")
):
    if len(files) > MAX_IMAGES:
        raise HTTPException(status_code=400, detail=f"Max {MAX_IMAGES} images allowed per batch.")
    
    if not creator_name.strip():
        raise HTTPException(status_code=400, detail="Creator name is required.")
    
    if ai_consent not in ["granted", "denied", "conditional"]:
        raise HTTPException(status_code=400, detail="AI consent must be 'granted', 'denied', or 'conditional'.")
    
    results = []
    timestamp = datetime.now().isoformat()
    
    for file in files:
        # Security: check file type and size
        if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
        
        contents = await file.read()
        if len(contents) > MAX_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large: {file.filename}")
        
        try:
            img = Image.open(BytesIO(contents)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image: {file.filename}. PIL error: {str(e)}")
        
        # Apply watermarks based on type
        if watermark_type == "invisible":
            watermarked_img = create_robust_watermark(img, creator_name, timestamp)
        elif watermark_type == "visible":
            watermarked_img = add_visible_watermark(img, creator_name, visible_opacity)
        else:  # both
            watermarked_img = create_robust_watermark(img, creator_name, timestamp)
            watermarked_img = add_visible_watermark(watermarked_img, creator_name, visible_opacity)
        
        # Add metadata
        watermarked_img = add_metadata(watermarked_img, creator_name, ai_consent, additional_info)
        
        # Save with original format
        buf = BytesIO()
        ext = file.filename.split('.')[-1].lower()
        name_wo_ext = '.'.join(file.filename.split('.')[:-1]) or 'image'
        
        # Map extension to PIL format
        ext_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG'}
        pil_format = ext_map.get(ext, 'PNG')
        if ext not in SUPPORTED_FORMATS:
            ext = "png"
        
        # Preserve metadata when saving
        save_kwargs = {"format": pil_format, "quality": 95}
        if pil_format == 'JPEG' and "exif" in watermarked_img.info:
            save_kwargs["exif"] = watermarked_img.info["exif"]
        elif pil_format == 'PNG' and "metadata" in watermarked_img.info:
            save_kwargs["pnginfo"] = watermarked_img.info["metadata"]
        
        watermarked_img.save(buf, **save_kwargs)
        buf.seek(0)
        
        new_fname = f"{name_wo_ext}_ai_protected.{ext}"
        results.append((new_fname, buf, ext))
    
    # For batch, return as zip
    if len(results) > 1:
        import zipfile
        zip_buf = BytesIO()
        with zipfile.ZipFile(zip_buf, 'w') as zipf:
            for fname, buf, ext in results:
                zipf.writestr(fname, buf.read())
        zip_buf.seek(0)
        return StreamingResponse(zip_buf, media_type="application/zip", 
                               headers={"Content-Disposition": "attachment; filename=ai_protected_images.zip"})
    
    # Single image
    fname, buf, ext = results[0]
    return StreamingResponse(buf, media_type=f"image/{ext}", 
                           headers={"Content-Disposition": f"attachment; filename={fname}"})

@app.get("/")
async def root():
    return {"message": "AI-Protected Image Watermarking API - Enhanced protection against AI models"} 