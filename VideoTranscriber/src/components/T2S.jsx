import React, { useEffect, useState } from "react";

export default function T2S({ summary }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [videoUrls, setVideoUrls] = useState([]);
  const [words, setWords] = useState([]);
  const [signImages, setSignImages] = useState({});
  const [fallbackMode, setFallbackMode] = useState(false); // Track if fallback mode is active

  useEffect(() => {fetchSign()}, [summary]);

  useEffect(() => 
  {
    const timeout = setTimeout(() => 
    {
      setCurrentIndex(i => i + 1);
      setFallbackMode(false); // Reset fallback mode for the next word
    }, 1750);
    return () => clearTimeout(timeout);
  }, [currentIndex]);

  function fetchSign() {
    fetch("http://127.0.0.1:5000/get_signs", {method: "POST",
                                              headers: { "Content-Type": "application/json" },
                                              body: JSON.stringify({ summary }),
                                             })
      .then((res) => res.json())
      .then((data) => 
      {
        setVideoUrls(data.videoUrls);
        setWords(data.words);
        setSignImages(data.signImages);
      })
      .catch((error) => console.log("Error=", error));
  }

  function handleVideoError() 
  {
    console.log("Video unavailable, switching to fallback images.");
    setFallbackMode(true); // Activate fallback mode when video fails
  }

  return (
    <div>
      <h2>word={words[currentIndex]}</h2>

      {/* Video Player */}
      {!fallbackMode && videoUrls[currentIndex] && (
        <video id="videoPlayer" width="400" height="400" controls autoPlay>
          <source src={videoUrls[currentIndex]} type="video/mp4" onError={handleVideoError}/>
        </video>
      )}

      {/* Fallback: Character-wise Images */}
      {fallbackMode && (
        <div id="signImages" className="flex gap-5">
        {words[currentIndex] && words[currentIndex].split("").map((char, index) => 
        (
          <div key={index} className="text-center">
            <h2>{char}</h2>
            {signImages[char] && <img src={signImages[char]} className="w-[100px] h-[100px]" alt={char}/>}
          </div>
        ))}
        </div>
      )}
    </div>
  );
}
