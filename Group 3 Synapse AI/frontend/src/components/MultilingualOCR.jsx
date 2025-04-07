import React, { useState, useEffect, useCallback } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, MessageSquare } from "lucide-react";
import "./MultilingualOCR.css";

const MultilingualOCR = () => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("eng");
  const [isLoading, setIsLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [extractedTexts, setExtractedTexts] = useState(() => {
    return JSON.parse(localStorage.getItem("ocrHistory")) || [];
  });

  const navigate = useNavigate();

  useEffect(() => {
    localStorage.setItem("ocrHistory", JSON.stringify(extractedTexts));
  }, [extractedTexts]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type.startsWith('image/') || droppedFile.type === 'application/pdf')) {
      setFile(droppedFile);
    } else {
      alert("Please upload an image or PDF file!");
    }
  }, []);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Please upload a file!");
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", language);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/ocr", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.text) {
        const newExtractedText = { 
          id: Date.now(), 
          text: data.text,
          fileName: file.name,
          timestamp: new Date().toLocaleString(),
          language: language
        };
        setExtractedTexts((prev) => [newExtractedText, ...prev]);
        navigate("/ocr-result", { state: { result: data.text, id: newExtractedText.id, language: language } });
      } else {
        alert("Error: " + (data.error || "Failed to extract text."));
      }
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="ocr-container">
        <div className="header-buttons">
          <Link to="/" className="back-button">
            <ArrowLeft />
          </Link>
        </div>
        <div className="upload-section">
          <h2 className="ocr-title">Document Text Extractor</h2>
          <p className="ocr-description">
            Extract text from images and PDFs in multiple languages
          </p>
          
          <form className="ocr-form" onSubmit={handleSubmit}>
            <div 
              className={`drop-zone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="drop-zone-content">
                {file ? (
                  <>
                    <div className="file-info">
                      <i className="file-icon">📄</i>
                      <span className="file-name">{file.name}</span>
                    </div>
                    <button 
                      type="button" 
                      className="remove-file"
                      onClick={() => setFile(null)}
                    >
                      ✕
                    </button>
                  </>
                ) : (
                  <>
                    <i className="upload-icon">📁</i>
                    <p>Drag and drop your file here or</p>
                    <label className="file-input-label">
                      Browse Files
                      <input
                        type="file"
                        accept="image/*,application/pdf"
                        onChange={handleFileChange}
                        className="hidden-input"
                      />
                    </label>
                  </>
                )}
              </div>
            </div>

            <div className="form-controls">
              <div className="language-select">
                <label htmlFor="language" className="form-label">Document Language</label>
                <select
                  id="language"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="form-input"
                >
                  <option value="eng">English</option>
                  <option value="spa">Spanish</option>
                  <option value="mal">Malayalam</option>
                  <option value="fra">French</option>
                </select>
              </div>

              <button type="submit" className="submit-button" disabled={isLoading || !file}>
                {isLoading ? (
                  <>
                    <span className="spinner"></span>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <span className="button-icon">📝</span>
                    <span>Extract Text</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {extractedTexts.length > 0 && (
        <aside className="history-section">
          <h3 className="history-title">Recent Extractions</h3>
          <Link to="/all-documents-chat" className="all-docs-chat-button">
            <MessageSquare size={20} />
            Chat with All Documents
          </Link>
          <div className="ocr-cards-container">
            {extractedTexts.map((item) => (
              <div key={item.id} className="ocr-card">
                <div className="ocr-card-header">
                  <span className="file-icon">📄</span>
                  <span className="file-name">{item.fileName || 'Document'}</span>
                </div>
                <div className="ocr-card-body">
                  <p className="ocr-card-text">{item.text.substring(0, 100)}...</p>
                  <div className="ocr-card-meta">
                    <span className="timestamp">{item.timestamp}</span>
                    <span className="language-tag">{item.language}</span>
                  </div>
                  <button 
                    className="ocr-view-button" 
                    onClick={() => navigate("/ocr-result", { state: { result: item.text, id: item.id, language: item.language } })}
                  >
                    View Full Text
                  </button>
                </div>
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
};

export default MultilingualOCR;
