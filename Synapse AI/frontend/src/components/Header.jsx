import React from "react";
import { Link } from "react-router-dom";
import { Brain } from "lucide-react";

function Header() {
    return (
        <header className="header">
            <nav className="nav-container">
                <Link to="/" className="logo">
                    <Brain size={32} />
                    <span>Synapse</span>
                </Link>
                <div className="nav-links">
                    <a href="#features">Features</a>
                    <a href="#use-cases">Use Cases</a>
                    <Link to="/ocr" className="primary">Try Now</Link>
                </div>
            </nav>
        </header>
    );
}

export default Header;
