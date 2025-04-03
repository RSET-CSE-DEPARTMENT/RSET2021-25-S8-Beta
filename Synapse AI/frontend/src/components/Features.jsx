import React from "react";
import { FileText, MessageSquare, Globe, Volume2 } from "lucide-react";

function Features() {
    const features = [
        {
            icon: <FileText size={28} />,
            title: "OCR Technology",
            description: "Transform any text image or handwritten notes into searchable digital content with our advanced AI technology. Support for multiple languages and formats.",
        },
        {
            icon: <MessageSquare size={28} />,
            title: "AI Chat Assistant",
            description: "Engage with your documents through our intelligent chatbot. Get instant answers, summaries, and insights from your content using advanced AI.",
        },
        {
            icon: <Globe size={28} />,
            title: "Multilingual Support",
            description: "Break language barriers with support for 100+ languages. Automatically detect and process text in different languages with high accuracy.",
        },
        {
            icon: <Volume2 size={28} />,
            title: "Text-to-Speech",
            description: "Listen to your documents with natural-sounding voice synthesis. Multiple voices and languages available for an enhanced learning experience.",
        },
    ];

    return (
        <section id="features" className="features">
            <div className="section-header">
                <h2>Powerful Features</h2>
                <p>Everything you need to digitize, understand, and interact with your documents</p>
            </div>
            <div className="features-grid">
                {features.map((feature, index) => (
                    <div key={index} className="feature-card">
                        <div className="icon">{feature.icon}</div>
                        <h3>{feature.title}</h3>
                        <p>{feature.description}</p>
                    </div>
                ))}
            </div>
        </section>
    );
}

export default Features;
