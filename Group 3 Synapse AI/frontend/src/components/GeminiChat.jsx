import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Volume2 } from "lucide-react"; // Speaker Icon
import "./GeminiChat.css";

const GeminiChat = ({ extractedText, docId }) => {
  const [userMessage, setUserMessage] = useState("");
  const [chatbotMessages, setChatbotMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [speakingMessage, setSpeakingMessage] = useState(null); // Track speaking message
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatbotMessages, isLoading]);

  useEffect(() => {
    if (!docId) return;

    const chatKey = `chatHistory_${docId}`;
    const storedChat = JSON.parse(localStorage.getItem(chatKey)) || [];
    setChatbotMessages(storedChat);
  }, [docId]);

  useEffect(() => {
    if (!docId || chatbotMessages.length === 0) return;

    const chatKey = `chatHistory_${docId}`;
    localStorage.setItem(chatKey, JSON.stringify(chatbotMessages));
  }, [chatbotMessages, docId]);

  const handleSendMessage = async () => {
    if (userMessage.trim() === "") return;

    const newMessages = [...chatbotMessages, { sender: "user", message: userMessage }];
    setChatbotMessages(newMessages);
    setUserMessage("");
    setIsLoading(true);

    try {
      const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
      const response = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
        {
          contents: [
            {
              parts: [
                { text: `Document Context:\n${extractedText}\n\nUser query: ${userMessage}` },
              ],
            },
          ],
        }
      );

      const botResponse =
        response.data?.candidates?.[0]?.content?.parts?.[0]?.text || "No response received.";

      const updatedMessages = [...newMessages, { sender: "chatbot", message: botResponse }];
      setChatbotMessages(updatedMessages);
      localStorage.setItem(`chatHistory_${docId}`, JSON.stringify(updatedMessages));
    } catch (error) {
      console.error("Error fetching response:", error);
      setChatbotMessages([
        ...newMessages,
        { sender: "chatbot", message: "Sorry, I couldn't process your request." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setUserMessage(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 150)}px`;
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSpeak = (text) => {
    if (speakingMessage === text) {
      // If the same message is currently being spoken, stop it
      window.speechSynthesis.cancel();
      setSpeakingMessage(null);
      return;
    }
  
    // Stop any ongoing speech before starting a new one
    window.speechSynthesis.cancel();
    setSpeakingMessage(text);
  
    const speakText = () => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.2; // Adjust speed
  
      // Ensure voices are available
      const voices = window.speechSynthesis.getVoices();
      const selectedVoice = voices.find(v => v.name.includes("Google UK English Female"));
  
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      } else {
        console.warn("Preferred voice not found. Using default voice.");
      }
  
      // Start speech
      window.speechSynthesis.speak(utterance);
  
      utterance.onend = () => setSpeakingMessage(null);
      utterance.onerror = (err) => {
        console.error("Speech synthesis error:", err);
        setSpeakingMessage(null);
      };
    };
  
    // If voices are not available yet, wait for them to load
    if (window.speechSynthesis.getVoices().length === 0) {
      window.speechSynthesis.onvoiceschanged = speakText;
    } else {
      speakText();
    }
  };
  
  return (
    <div className="gemini-chat-container">
      <div className="chat-messages">
        {chatbotMessages.length === 0 ? (
          <div className="message chatbot-message">
            <div className="chatbot-response">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {`👋 Hello! I'm SynapseAI, and I'm here to help you understand and analyze the extracted text. Here's what I can do for you:

* Ask me questions about the text
* Request a summary of the content
* Get explanations of specific parts
* Ask for key points or main ideas
* Request analysis or insights
* Click the speaker icon 🔊 to hear my responses

Feel free to start by asking any question about the text!`}
              </ReactMarkdown>
              <button className="tts-button" onClick={() => handleSpeak("Hello! I'm your AI assistant, and I'm here to help you understand and analyze the extracted text. Here's what I can do for you: Ask me questions about the text, request a summary of the content, get explanations of specific parts, ask for key points or main ideas, request analysis or insights, and click the speaker icon to hear my responses. Feel free to start by asking any question about the text!")}>
                <Volume2 size={16} />
              </button>
            </div>
          </div>
        ) : (
          chatbotMessages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender === "user" ? "user-message" : "chatbot-message"}`}>
              {msg.sender === "chatbot" ? (
                <div className="chatbot-response">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.message}</ReactMarkdown>
                  <button className="tts-button" onClick={() => handleSpeak(msg.message)}>
                    <Volume2 size={16} className={speakingMessage === msg.message ? "active" : ""} />
                  </button>
                </div>
              ) : (
                msg.message
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div className="loading-indicator">
            <span className="dot"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input">
        <textarea
          value={userMessage}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          rows="1"
          className="chat-textarea"
        ></textarea>
        <button onClick={handleSendMessage} disabled={isLoading || !userMessage.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

export default GeminiChat;
