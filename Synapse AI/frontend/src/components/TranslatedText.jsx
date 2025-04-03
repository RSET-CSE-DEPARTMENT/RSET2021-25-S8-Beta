import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { ArrowLeft } from "lucide-react";
import "./TranslatedText.css";

const languageMap = {
  "eng": "English",
  "spa": "Spanish",
  "mal": "Malayalam",
  "fra": "French",
  "auto": "Auto-detected"
};

const formatText = (text) => {
  // Split text into paragraphs (double newlines)
  const paragraphs = text.split(/\n\s*\n/);
  
  // Process each paragraph
  return paragraphs.map((paragraph, index) => {
    // Replace single newlines with spaces within paragraphs
    const formattedParagraph = paragraph.replace(/\n/g, ' ').trim();
    return formattedParagraph;
  }).filter(paragraph => paragraph.length > 0);
};

const TranslatedText = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { result, language } = location.state || { result: "", language: "auto" };
  const [translatedText, setTranslatedText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const translateText = async () => {
      if (!result) return;

      setIsLoading(true);
      setError("");

      try {
        const response = await axios.post(
          "http://localhost:8000/api/translate",
          {
            text: result,
            source_lang: language,
          }
        );

        setTranslatedText(response.data.translated_text);
      } catch (err) {
        console.error("Translation error:", err);
        setError("Failed to translate text. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };

    translateText();
  }, [result, language]);

  const sourceLanguage = languageMap[language] || "Unknown";
  const showLanguageInfo = language !== "auto";

  const formattedOriginalText = formatText(result);
  const formattedTranslatedText = formatText(translatedText);

  return (
    <div className="translated-text-page">
      <header className="translated-text-header">
        <h1>Translated Text</h1>
        <button 
          onClick={() => navigate("/ocr-result", { 
            state: { result, id: location.state?.id, language } 
          })} 
          className="back-button"
        >
          <ArrowLeft />
        </button>
      </header>

      <div className="translated-text-content">
        {isLoading ? (
          <div className="loading">Translating...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : (
          <div className="translated-text-container">
            <div className="text-section">
              <h2>Original Text</h2>
              {showLanguageInfo && (
                <div className="language-info">
                  From: <span className="language-tag">{sourceLanguage}</span>
                </div>
              )}
              <div className="original-text">
                {formattedOriginalText.map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
            </div>
            
            <div className="text-section">
              <h2>Translated Text</h2>
              <div className="language-info">
                To: <span className="language-tag">English</span>
              </div>
              <div className="translated-text">
                {formattedTranslatedText.map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TranslatedText;
