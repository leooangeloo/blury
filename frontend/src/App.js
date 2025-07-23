import React, { useState } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000/watermark';
const MAX_IMAGES = 5;
const MAX_SIZE_MB = 10;
const SUPPORTED_FORMATS = ['image/png', 'image/jpeg', 'image/jpg'];

function App() {
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [downloadName, setDownloadName] = useState('');
  const [creatorName, setCreatorName] = useState('');
  const [watermarkType, setWatermarkType] = useState('both');
  const [opacity, setOpacity] = useState(0.3);
  const [aiConsent, setAiConsent] = useState('denied');
  const [additionalInfo, setAdditionalInfo] = useState('');

  const handleFiles = (e) => {
    setError('');
    let selected = Array.from(e.target.files);
    if (selected.length > MAX_IMAGES) {
      setError(`Max ${MAX_IMAGES} images allowed.`);
      return;
    }
    for (let file of selected) {
      if (!SUPPORTED_FORMATS.includes(file.type)) {
        setError(`Unsupported file type: ${file.type}`);
        return;
      }
      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        setError(`File too large: ${file.name}`);
        return;
      }
    }
    setFiles(selected);
    setPreviews(selected.map(f => URL.createObjectURL(f)));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!creatorName.trim()) {
      setError('Please enter a creator name.');
      return;
    }
    setError('');
    setLoading(true);
    setDownloadUrl(null);
    setDownloadName('');
    
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    formData.append('creator_name', creatorName);
    formData.append('watermark_type', watermarkType);
    formData.append('visible_opacity', opacity);
    formData.append('ai_consent', aiConsent);
    formData.append('additional_info', additionalInfo);
    
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || 'Processing failed.');
        setLoading(false);
        return;
      }
      const blob = await res.blob();
      let contentDisp = res.headers.get('Content-Disposition');
      let fname = '';
      if (contentDisp) {
        let match = contentDisp.match(/filename="?([^";]+)"?/);
        if (match) fname = match[1];
      }
      if (!fname) {
        // fallback: use first file name with _ai_protected
        if (files.length === 1) {
          const orig = files[0].name;
          const ext = orig.split('.').pop();
          const base = orig.replace(/\.[^.]+$/, '');
          fname = `${base}_ai_protected.${ext}`;
        } else {
          fname = 'ai_protected_images.zip';
        }
      }
      setDownloadUrl(URL.createObjectURL(blob));
      setDownloadName(fname);
    } catch (err) {
      setError('Network or server error.');
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <h2>Blury</h2>
      <p className="subtitle">
        AI-Protected Image Watermarking App
      </p>
      
      <div className="feature-card">
        <h3>🛡️ Enhanced Protection Features</h3>
        <ul className="feature-list">
          <li>Multi-channel steganography (harder to remove)</li>
          <li>Adversarial perturbations (confuses AI models)</li>
          <li>Frequency domain modifications (DCT-based)</li>
          <li>Invisible grid patterns (additional protection)</li>
          <li>Multiple visible watermarks (better coverage)</li>
        </ul>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="creatorName">
            👤 Creator Name *
          </label>
          <input
            id="creatorName"
            type="text"
            value={creatorName}
            onChange={(e) => setCreatorName(e.target.value)}
            placeholder="Enter your name or artist name"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="aiConsent">
            🤖 AI Training Consent *
          </label>
          <select
            id="aiConsent"
            value={aiConsent}
            onChange={(e) => setAiConsent(e.target.value)}
          >
            <option value="denied">❌ Denied - Do not use for AI training</option>
            <option value="conditional">⚠️ Conditional - Use only with permission</option>
            <option value="granted">✅ Granted - Allow AI training</option>
          </select>
          <span className="help-text">
            This consent tag will be embedded in the image metadata for AI models to read
          </span>
        </div>

        <div className="form-group">
          <label htmlFor="additionalInfo">
            📝 Additional Information (Optional)
          </label>
          <textarea
            id="additionalInfo"
            value={additionalInfo}
            onChange={(e) => setAdditionalInfo(e.target.value)}
            placeholder="Any additional terms, contact info, or licensing details..."
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="watermarkType">
            🛡️ Protection Level
          </label>
          <select
            id="watermarkType"
            value={watermarkType}
            onChange={(e) => setWatermarkType(e.target.value)}
          >
            <option value="both">🛡️ Maximum Protection (Invisible + Visible)</option>
            <option value="invisible">🔒 Invisible Only (Stealth Protection)</option>
            <option value="visible">👁️ Visible Only (Deterrent Protection)</option>
          </select>
        </div>

        {watermarkType !== 'invisible' && (
          <div className="form-group">
            <label htmlFor="opacity">
              🎨 Visible Watermark Opacity: {Math.round(opacity * 100)}%
            </label>
            <div className="range-container">
              <input
                id="opacity"
                type="range"
                min="0.1"
                max="0.8"
                step="0.1"
                value={opacity}
                onChange={(e) => setOpacity(parseFloat(e.target.value))}
              />
            </div>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="fileInput">
            📁 Select Images (Max {MAX_IMAGES})
          </label>
          <input
            id="fileInput"
            type="file"
            accept="image/png, image/jpeg, image/jpg"
            multiple
            onChange={handleFiles}
            disabled={loading}
          />
          <span className="help-text">
            Supported formats: PNG, JPG, JPEG (Max {MAX_SIZE_MB}MB each)
          </span>
        </div>

        {previews.length > 0 && (
          <div className="form-group">
            <label>🖼️ Image Previews</label>
            <div className="image-preview">
              {previews.map((src, i) => (
                <img 
                  key={i} 
                  src={src} 
                  alt={`preview-${i}`} 
                  className="preview-image"
                />
              ))}
            </div>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            <span>⚠️</span>
            {error}
          </div>
        )}
        
        <button type="submit" disabled={loading || files.length === 0 || !creatorName.trim()}>
          {loading ? (
            <>
              <span className="loading"></span>
              Processing...
            </>
          ) : (
            '🛡️ Apply AI Protection'
          )}
        </button>
      </form>
      
      {downloadUrl && (
        <div className="download-section">
          <h3>✅ Protection Complete!</h3>
          <p>Your images have been successfully protected with AI-resistant watermarks.</p>
          <a href={downloadUrl} download={downloadName} className="download-link">
            <span>⬇️</span>
            Download AI-Protected {files.length > 1 ? 'Images (zip)' : 'Image'}
          </a>
        </div>
      )}
      
      <footer>
        <p><strong>🔒 Privacy & Security:</strong> No images are saved. All processing is local and secure.</p>
        <p><strong>🛡️ Enhanced Protection:</strong> Uses multiple techniques to resist AI model processing.</p>
        <p><strong>👁️ Visible Watermarks:</strong> Add multiple copyright notices for better coverage.</p>
        <p><strong>📋 Metadata:</strong> Includes AI training consent tags that can be read by AI models.</p>
        <p><strong>⚠️ Note:</strong> While this provides enhanced protection, no method is 100% foolproof against all AI models.</p>
        <hr style={{ margin: '1.5rem 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />
        <p style={{ marginTop: '1rem', fontWeight: '600', color: '#2d3748' }}>
          Copyright © Leo Angelo Genota. All Rights Reserved.
        </p>
      </footer>
    </div>
  );
}

export default App;
