// src/components/Home.jsx
import React from 'react';
import Header from './Header'
import Hero from './Hero';
import Features from './Features'; 
import UseCases from './UseCases';
import './Home.css';

const Home = () => {
    return (
        <div>
            <Header />
            <Hero />
            <Features />
            <UseCases />
        </div>
    );
};

export default Home;
