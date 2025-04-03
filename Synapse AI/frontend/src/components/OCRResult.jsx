import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import GeminiChat from "./GeminiChat";
import { Volume2, ArrowLeft, Globe } from "lucide-react"; 
import "./OCRResult.css";

const OCRResult = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { result, id, language } = location.state || { result: "", id: null, language: "auto" };

  const [extractedTexts, setExtractedTexts] = useState(() => {
    return JSON.parse(localStorage.getItem("ocrHistory")) || [];
  });

  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    if (result && id) {
      const exists = extractedTexts.some((entry) => entry.id === id);
      if (!exists) {
        const newExtractedText = { id, text: result, language };
        const updatedTexts = [newExtractedText, ...extractedTexts];

        setExtractedTexts(updatedTexts);
        localStorage.setItem("ocrHistory", JSON.stringify(updatedTexts));
      }
    }
  }, [result, id, language]);

  const handleSpeak = (text) => {
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }

    // Split text into sentences
    const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
    let currentIndex = 0;

    const speakNextSentence = () => {
      if (currentIndex >= sentences.length) {
        setSpeaking(false);
        return;
      }

      const utterance = new SpeechSynthesisUtterance(sentences[currentIndex].trim());
      utterance.rate = 1.2;

      // Ensure voices are available
      const voices = window.speechSynthesis.getVoices();
      const selectedVoice = voices.find(v => v.name.includes("Google UK English Female"));

      if (selectedVoice) {
        utterance.voice = selectedVoice;
      } else {
        console.warn("Preferred voice not found. Using default voice.");
      }

      utterance.onend = () => {
        currentIndex++;
        speakNextSentence();
      };

      utterance.onerror = (err) => {
        console.error("Speech synthesis error:", err);
        setSpeaking(false);
      };

      window.speechSynthesis.speak(utterance);
    };

    // If voices are not available yet, wait for them to load
    if (window.speechSynthesis.getVoices().length === 0) {
      window.speechSynthesis.onvoiceschanged = () => {
        setSpeaking(true);
        speakNextSentence();
      };
    } else {
      setSpeaking(true);
      speakNextSentence();
    }
  };

  return (
    <div className="ocr-result-page">
      <header className="ocr-result-header">
        <h1>OCR Results</h1>
        <button onClick={() => navigate("/ocr")} className="back-button">
          <ArrowLeft />
        </button>
      </header>

      <div className="ocr-result-content">
        <div className="extracted-text-section">
          <div className="extracted-text-header">
            <h2>Extracted Text</h2>
            <div className="button-group">
              <button 
                className="translate-button" 
                onClick={() => navigate("/translated", { state: { result, id, language } })}
              >
                <Globe size={20} />
                Translate Text
              </button>
              <button className="tts-button" onClick={() => handleSpeak(result)}>
                <Volume2 size={20} className={speaking ? "active" : ""} />
              </button>
            </div>
          </div>
          <div className="ocr-text-container">
            <pre>{result}</pre>
          </div>
        </div>

        <div className="chat-section">
          <h2>Chat With Your Document</h2>
          <GeminiChat extractedText={result} docId={id} />
        </div>
      </div>
    </div>
  );
};

export default OCRResult;
