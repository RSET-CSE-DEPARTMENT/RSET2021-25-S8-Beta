import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./components/Home";
import MultilingualOCR from "./components/MultilingualOCR";
import OCRResult from "./components/OCRResult";
import GeminiChat from "./components/GeminiChat";
import TranslatedText from "./components/TranslatedText";
import AllDocumentsChat from "./components/AllDocumentsChat";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ocr" element={<MultilingualOCR />} />
        <Route path="/ocr-result" element={<OCRResult />} />
        <Route path="/chat" element={<GeminiChat />} />
        <Route path="/translated" element={<TranslatedText />} />
        <Route path="/all-documents-chat" element={<AllDocumentsChat />} />
      </Routes>
    </Router>
  );
}

export default App;
