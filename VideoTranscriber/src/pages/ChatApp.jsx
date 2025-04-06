import React, { useState, useEffect } from "react";

const botResponses = [
  { type: "text", content: "Hello! How can I help you today?" },
  { type: "image", content: "https://source.unsplash.com/200x200/?nature" },
  { type: "video", content: "https://www.w3schools.com/html/mov_bbb.mp4" },
  { type: "audio", content: "https://www.w3schools.com/html/horse.mp3" },
  { type: "text", content: "That's interesting! Tell me more." }
];

export default function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;
    const newUserMessage = { type: "text", content: input, sender: "user" };
    setMessages([...messages, newUserMessage]);
    setInput("");

    setTimeout(() => {
      const botMessage = botResponses[Math.floor(Math.random() * botResponses.length)];
      setMessages((prev) => [...prev, { ...botMessage, sender: "bot" }]);
    }, 1000);
  };

  return (
    <div className="max-w-md mx-auto bg-gray-100 p-4 rounded-lg shadow-lg">
      <div className="h-80 overflow-y-auto p-2 space-y-3">
        {messages.map((msg, index) => (
          <div key={index} className={`p-2 rounded-lg ${msg.sender === "user" ? "bg-blue-500 text-white self-end" : "bg-gray-300 text-black self-start"}`}>
            {msg.type === "text" && <p>{msg.content}</p>}
            {msg.type === "image" && <img src={msg.content} alt="bot media" className="w-40 rounded-lg" />}
            {msg.type === "video" && <video src={msg.content} controls className="w-40 rounded-lg" />}
            {msg.type === "audio" && <audio src={msg.content} controls className="w-full" />}
          </div>
        ))}
      </div>
      <div className="flex mt-2">
        <input
          className="flex-1 p-2 border rounded-l-lg"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button className="bg-blue-500 text-white px-4 rounded-r-lg" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}
