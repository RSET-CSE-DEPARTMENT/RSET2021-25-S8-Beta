import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import GeminiChat from "./GeminiChat";
import { ArrowLeft } from "lucide-react";
import "./AllDocumentsChat.css";

const AllDocumentsChat = () => {
  const navigate = useNavigate();
  const [allTexts, setAllTexts] = useState([]);
  const [combinedText, setCombinedText] = useState("");

  useEffect(() => {
    // Get all scanned documents from localStorage
    const extractedTexts = JSON.parse(localStorage.getItem("ocrHistory")) || [];
    setAllTexts(extractedTexts);

    // Combine all texts with metadata
    const combined = extractedTexts
      .map((doc) => {
        const timestamp = new Date(doc.timestamp).toLocaleString();
        return `Document: ${doc.name} (${doc.language}, ${timestamp}):\n${doc.text}\n\n`;
      })
      .join("---\n\n");

    setCombinedText(combined);
  }, []);

  return (
    <div className="all-docs-chat-page">
      <header className="all-docs-chat-header">
        <h1>Chat with All Documents</h1>
        <button onClick={() => navigate("/")} className="all-docs-back-button">
          <ArrowLeft />
        </button>
      </header>

      <div className="all-docs-chat-content">
        <div className="all-docs-summary">
          <h2>Available Documents</h2>
          <div className="all-docs-list">
            {allTexts.map((doc) => (
              <div key={doc.id} className="all-docs-card">
                {/* <div className="all-docs-info">
                  <span className="all-docs-number">{doc.name}</span>
                  <span className="all-docs-language">{doc.language}</span>
                  <span className="all-docs-date">{new Date(doc.timestamp).toLocaleString()}</span>
                </div> */}
                <div className="all-docs-preview">
                  {doc.text.substring(0, 300)}...
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="all-docs-chat-section">
          <GeminiChat extractedText={combinedText} docId="all_documents" />
        </div>
      </div>
    </div>
  );
};

export default AllDocumentsChat; 