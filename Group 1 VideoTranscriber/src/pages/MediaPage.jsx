import React, { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import YouTube from 'react-youtube';
import T2S from '../components/T2S'

export default function MediaPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const {video, urlID,transcript} = location.state||{};

  const [textContent, setTextContent] = useState(transcript);
  const [summary, setSummary] = useState('');
  const [transSummary, setTransSummary] = useState('');
  const [showTranslate, setShowTranslate] = useState(false);
  const [search, setSearch] = useState('');
  const [keywords,setKeywords] = useState(null);   //List of keywords
  const [sentFound, setSentFound] = useState(null); //List of sentences with the selected keyword
  const [showSign, setShowSign] = useState(false);
  const [videoUrls, setVideoUrls] = useState([]);
  const [option, setOption] = useState(0);
  const [showPopup, setShowPopup] = useState(false);
  const [showSummaryProgress, setShowSummaryProgress] = useState(false);
  const [showEdit, setShowEdit] = useState(false);

  const searchFilterRef = useRef(null);

  const colors=[['bg-blue-400 hover:bg-blue-300 active:bg-blue-500','bg-blue-300'],
                ['bg-purple-400 hover:bg-purple-300 active:bg-purple-500','bg-purple-300'],
                ['bg-green-400 hover:bg-green-300 active:bg-green-500','bg-green-300']];
  const n=colors.length;

  useEffect(()=>
  {
    setShowPopup(false);
    setShowSummaryProgress(false);
    if(option) summarize();
  },[option]);

  function VideoPlayer({vid})
  {
   return (
    <div className=' shadow-[0px_3px_3px_black] overflow-hidden rounded-lg'> 
      <YouTube videoId={vid} opts={{height: '400', width: '640', playerVars: {autoplay: 0, mute: 1}}} className='rounded'/>
    </div>
  );
  }

  function handleSummaryType(type)
  {
    setOption(type);
    setShowPopup(!showPopup);
    setShowSummaryProgress(!showSummaryProgress);
  }

  function summarize()
  {
    if(![1,2].includes(option)) return;
    fetch('http://localhost:5000/summarization', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({transcript, option}),
    })
      .then(res => res.json())
      .then(data => {
        setShowPopup(false)
        setShowSummaryProgress(false);
        setSummary(data.summary)
        setKeywords(data.searchlist)
        setSentFound(data.sentFound)
        setTransSummary(data.translation)
    });
  }

  function handleTranscriptEdit(e)
  {
    e.preventDefault();
   setTextContent(e.target.value)
   setShowEdit(true)
  }

  function handleSummaryEdit(e)
  {
   e.preventDefault();
   setSummary(e.target.value)
   setShowEdit(true)
  }

  const save = () => setShowEdit(false);

  function Read()
  {
    const utterance = new SpeechSynthesisUtterance(transcript);
    utterance.lang = 'en-US';
    utterance.rate = 1; // Speed
    window.speechSynthesis.speak(utterance);
  }

  function handleScrollToSection(sectionRef)
  {
   if(sectionRef.current) sectionRef.current.scrollIntoView({behavior:"smooth"});
  }

  function SaF()
  {

    fetch("http://localhost:5000/SearchAndFilter",{method:'POST',
                                                   headers: { 'Content-Type': 'application/json' }, 
                                                   body: JSON.stringify({summary, search})})
    .then(res => res.json())
    .then(data=>
    {
      console.log("Message from backend: ",data.message)
      setSentFound(data.sentence)
    })
  }

  return (
    <div>
        {/* Header button */}
        <div className='flex justify-end gap-5 p-3 border border-gray-200 '>
          <button className='p-2 rounded bg-blue-400 hover:bg-blue-300 active:bg-blue-500 w-[200px]' onClick={()=>handleScrollToSection(searchFilterRef)}>Search and filtering</button>
          <button className='p-2 rounded bg-purple-400 hover:bg-purple-300 active:bg-purple-500 w-[200px]' onClick={()=>navigate('/questionanswer',{state:{summary, keywords}})}>Test what you know!</button>
          <button className='p-2 rounded bg-green-400 hover:bg-green-300 active:bg-green-500 w-[200px]'>3</button>
        </div>

        <div className='flex flex-col gap-5 p-10'>
          <div className='flex gap-5'>
            {video&&<video src={URL.createObjectURL(video)} controls autoPlay className='rounded w-[500px] shadow-[0px_3px_3px_black]'></video>}
            {(urlID) && <VideoPlayer vid={urlID}/>}
            {showSign&&<div><T2S summary={summary}/></div>}
          </div>

          {/* Accessibility button */}
          <div className='flex gap-5'>
            <button className='p-3 rounded bg-blue-400 hover:bg-blue-300 active:bg-blue-500 w-[200px]' onClick={()=>setShowPopup(!showPopup)}>Summarize</button>
            <button className='p-3 rounded bg-purple-400 hover:bg-purple-300 active:bg-purple-500 w-[200px]' onClick={()=>setShowTranslate(!showTranslate)}>Auto translate</button>
            <button className='p-3 rounded bg-green-400 hover:bg-green-300 active:bg-green-500 w-[200px]' onClick={()=>setShowSign(!showSign)}>Show sign language</button>
            <button className='p-3 rounded bg-green-400 hover:bg-green-300 active:bg-green-500 w-[200px]' onClick={Read}>Read</button>
            {showEdit&&<button className='p-3 rounded bg-green-300 w-28' onClick={save}>Edit</button>}
          </div>

          <div className='flex flex-col gap-3'>
            <h1 className='font-bold'>Transcript</h1>
            <textarea value={textContent} onChange={(e)=>handleTranscriptEdit(e)} className=' w-[95%] min-h-[120px] resize-y'/>
          </div>
          
          {/* Show summary */}
          {summary&&
           <div>
            <h1 className='font-bold'>Summary</h1>
            <textarea value={summary} onChange={(e)=>handleSummaryEdit(e)} className=' w-[95%] min-h-[120px] resize-y'/>
           </div>}
          
           {/* Show summary */}
           {showTranslate&&(!transSummary ? alert("Already in English") :
           <div>
            <h1 className='font-bold'>Translated summary</h1>
            <textarea value={transSummary} onChange={(e)=>handleSummaryEdit(e)} className=' w-[95%] min-h-[120px] resize-y'/>
           </div>)}

           {/* Search and Filtering */}
           <div ref={searchFilterRef} className='flex flex-col gap-5'>
            <div className='flex flex-col gap-2'>
              <h1 className='font-bold'>Search</h1>
              <h2>For you</h2>
              {keywords&&<div className='flex flex-wrap gap-5 m-2'>
              {
                keywords.map((item,index)=>
                (
                 <div key={index} className={`flex justify-evenly items-center gap-2 rounded-full p-2 ${colors[index%n][0]} w-auto shadow-[0px_3px_3px_gray] cursor-pointer`} onClick={()=>setSearch(item[0])}>
                  <div>{item[0]}</div>
                  <div className={`flex justify-center items-center p-2 rounded-full shadow-[0px_3px_3px_gray] w-[20px] h-[20px] text-center ${colors[index%n][1]}`}>{item[1]}</div>
                 </div>
                ))
              }
              </div>}
            </div>
            <div className='flex gap-5'>
              <input type="text" placeholder='Enter keyword' value={search} onChange={(e)=>setSearch(e.target.value)} className='flex flex-auto p-2 text-xl w-[90%] rounded-[8px] border border-gray-300'/>
              <button onClick={SaF} className='p-3 rounded bg-blue-400 hover:bg-blue-300 active:bg-blue-500 w-[200px]'>Search</button>
            </div>
              {sentFound&&<h1 className='font-bold'>Result(s)</h1>}
              <div>{sentFound}</div>
           </div>
          
           {/* Summary option popup */}
           {showPopup&&
           <div className='fixed  top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 inset-50 bg-opacity-80 w-[500px] h-[200px] bg-purple-200 p-2 rounded-2xl'>
              <div className='absolute flex flex-col gap-3 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'>
                <h1 className='font-bold'>Select summarizer option</h1>
                <div className='flex gap-5'>
                  <button className='p-3 rounded bg-blue-400 w-28 cursor-pointer' onClick={()=>handleSummaryType(1)}>Extractive</button>
                  <button className='p-3 rounded bg-purple-400 w-28 cursor-pointer' onClick={()=>handleSummaryType(2)}>Abstractive</button>
                </div>
              </div>
           </div>}

           {/* Summary progress popup */}
           {showSummaryProgress&&
           <div className='fixed  top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 inset-50 opacity-80 w-[500px] h-[200px] bg-purple-200 p-2 rounded-2xl'>
              <div className='absolute flex flex-col gap-3 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'>
                <h1 className='font-bold text-white'>Summarizing.....</h1>
              </div>
           </div>}
        </div>
    </div>
  )
}
