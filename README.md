# 🛡️ Blury - AI-Protected Image Watermarking App

A comprehensive web application that protects artwork and images from AI models using advanced watermarking techniques.

## 🎯 Overview

Blury provides robust protection for digital artwork by combining multiple watermarking techniques specifically designed to resist AI model processing. It's designed for artists, photographers, and content creators who want to protect their work from unauthorized AI training and generation.

## ✨ Features

### 🛡️ Enhanced AI Protection
- **Multi-channel steganography** - Embeds watermarks in all RGB channels
- **Adversarial perturbations** - Subtle patterns that confuse AI models
- **Frequency domain modifications** - DCT-based watermarking for robustness
- **Invisible grid patterns** - Additional protection layers
- **Multiple visible watermarks** - Better coverage and deterrence

### 📝 Metadata Protection
- **AI training consent tags** - Machine-readable consent declarations
- **Creator information** - Embedded copyright and ownership data
- **Timestamped protection** - Proof of when protection was applied
- **EXIF/PNG metadata** - Industry-standard metadata embedding

### 🎨 Flexible Watermarking Options
- **Maximum Protection** - Combines invisible and visible watermarks
- **Stealth Protection** - Invisible watermarks only
- **Deterrent Protection** - Visible watermarks only
- **Customizable opacity** - Adjust visible watermark intensity

### 🔒 Security & Privacy
- **No server storage** - Images processed in memory only
- **Batch processing** - Up to 5 images at once
- **File validation** - Size and format checks
- **Original format preservation** - Maintains image quality

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blury
   ```

2. **Set up Python backend**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install fastapi uvicorn pillow torch torchvision python-multipart piexif opencv-python numpy
   ```

3. **Set up React frontend**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   # From the root directory
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`

2. **Start the frontend development server**
   ```bash
   # From the frontend directory
   npm start
   ```
   The web app will be available at `http://localhost:3000`

## 📖 Usage

### Basic Workflow

1. **Enter Creator Information**
   - Provide your name or artist name
   - Select AI training consent level (denied/conditional/granted)
   - Add optional additional information

2. **Choose Protection Level**
   - **Maximum Protection**: Best defense (invisible + visible)
   - **Stealth Protection**: Invisible only
   - **Deterrent Protection**: Visible only

3. **Upload Images**
   - Select up to 5 images (PNG, JPG, JPEG)
   - Maximum 10MB per image
   - Preview images before processing

4. **Apply Protection**
   - Click "Apply AI Protection"
   - Wait for processing to complete
   - Download protected images

### AI Training Consent Options

- **❌ Denied**: Explicitly prohibits AI training use
- **⚠️ Conditional**: Requires explicit permission before AI training
- **✅ Granted**: Allows AI training with the image

## 🔧 Technical Details

### Backend Architecture
- **FastAPI** - High-performance web framework
- **Pillow (PIL)** - Image processing and manipulation
- **OpenCV** - Computer vision and DCT operations
- **PyTorch** - Deep learning framework for adversarial techniques
- **piexif** - EXIF metadata handling

### Frontend Architecture
- **React** - User interface framework
- **Modern JavaScript** - ES6+ features
- **Responsive Design** - Works on desktop and mobile

### Protection Techniques

#### 1. Multi-Channel Steganography
```python
# Embeds watermarks in all RGB channels using 2 LSBs
for channel in [0, 1, 2]:  # RGB channels
    flat_channel = img_array[:, :, channel].flatten()
    for i, bit in enumerate(watermark_binary):
        flat_channel[i] = (flat_channel[i] & 0xFC) | (int(bit) * 3)
```

#### 2. Adversarial Perturbations
```python
# Adds subtle noise patterns that confuse AI models
noise_pattern = np.random.rand(height, width, 3) * 0.02
img_array = np.clip(img_array.astype(np.float32) + noise_pattern, 0, 255)
```

#### 3. Frequency Domain Modifications
```python
# DCT-based watermarking in frequency domain
dct_block = cv2.dct(block)
dct_block[3, 3] += 8  # Modify mid-frequency coefficients
idct_block = cv2.idct(dct_block)
```

### API Endpoints

- `POST /watermark` - Main watermarking endpoint
- `GET /` - API information

## 🛡️ Protection Effectiveness

### Limitations
- No protection method is 100% foolproof
- Effectiveness varies by AI model and processing method
- Some advanced AI models may still be able to process images
- Regular updates to protection techniques may be needed

## 🔍 Detection and Verification

### Watermark Detection
- Use specialized steganography detection tools
- Check EXIF metadata for embedded information
- Look for subtle patterns in image analysis

### Metadata Reading
```python
import piexif
from PIL import Image

# Read EXIF data
img = Image.open('protected_image.jpg')
exif_data = piexif.load(img.info['exif'])
creator = exif_data['0th'][piexif.ImageIFD.Artist].decode('utf-8')
ai_consent = exif_data['0th'][piexif.ImageIFD.DocumentName].decode('utf-8')
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is provided as-is for educational and protective purposes. While it implements advanced protection techniques, no method can guarantee 100% protection against all AI models. Users should:

- Understand the limitations of AI protection
- Use additional legal protections (copyright, licensing)
- Stay informed about evolving AI technologies
- Consider the balance between protection and usability

## 🆘 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check the documentation
- Review the technical details above

## 🔄 Updates

This application is actively maintained to keep up with:
- New AI model capabilities
- Improved protection techniques
- Security vulnerabilities
- User feedback and requests

---

**Made with ❤️ for artists and creators** 