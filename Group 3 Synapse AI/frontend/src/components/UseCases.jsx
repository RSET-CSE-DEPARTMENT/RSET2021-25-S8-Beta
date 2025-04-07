import React from "react";
import { GraduationCap, BookOpen, Microscope } from "lucide-react";

function UseCases() {
    const useCases = [
        {
            icon: <GraduationCap size={24} />,
            title: "Students",
            points: [
                "Convert textbook pages and handwritten notes to searchable digital format",
                "Record and transcribe lectures with high accuracy",
                "Create audio versions of study materials for on-the-go learning",
                "Get AI-powered explanations and summaries for complex topics",
                "Organize and search through your study materials effortlessly",
            ],
        },
        {
            icon: <BookOpen size={24} />,
            title: "Educators",
            points: [
                "Digitize teaching materials and handouts quickly",
                "Create accessible versions of content for all students",
                "Generate multilingual learning resources automatically",
                "Convert audio lectures to searchable text",
                "Track and analyze student engagement with materials",
            ],
        },
        {
            icon: <Microscope size={24} />,
            title: "Researchers",
            points: [
                "Digitize research papers and handwritten notes efficiently",
                "Extract and analyze data from documents and images",
                "Generate comprehensive summaries of long documents",
                "Collaborate with AI for deeper insights and connections",
                "Maintain a searchable database of research materials",
            ],
        },
    ];

    return (
        <section id="use-cases" className="use-cases">
            <div className="section-header">
                <h2>Who Can Benefit?</h2>
                <p>Discover how Synapse can transform your learning and work experience</p>
            </div>
            <div className="use-cases-grid">
                {useCases.map((useCase, index) => (
                    <div key={index} className="use-case-card">
                        <h3>
                            {useCase.icon}
                            {useCase.title}
                        </h3>
                        <ul>
                            {useCase.points.map((point, i) => (
                                <li key={i}>{point}</li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
        </section>
    );
}

export default UseCases;
