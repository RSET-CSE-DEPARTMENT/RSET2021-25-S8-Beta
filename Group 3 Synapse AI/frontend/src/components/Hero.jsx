import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Play } from "lucide-react";

function Hero() {
    return (
        <section className="hero">
            <span className="badge">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2v6m0 12v2M4.93 4.93l4.24 4.24m5.66 5.66 4.24 4.24M2 12h6m12 0h2M4.93 19.07l4.24-4.24m5.66-5.66 4.24-4.24" />
                </svg>
                Powered by Advanced AI
            </span>
            <h1>Transform Your Documents Into Interactive Knowledge</h1>
            <p>
                Convert any text, image, or handwritten note into searchable digital content. 
                Engage with your documents through AI-powered chat, multilingual support, and natural voice synthesis.
            </p>
            <div className="cta-buttons">
                <Link to="/ocr">
                    <button className="primary">
                        Try It Free
                        <ArrowRight size={20} />
                    </button>
                </Link>
                <button className="secondary">
                    <Play size={20} />
                    Watch Demo
                </button>
            </div>
        </section>
    );
}

export default Hero;
