import React, { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
// import loader from '../assets/VTLoader.gif'

export default function TranscriptionOptionPage() {

  
  const navigate = useNavigate();
  const location = useLocation();
  const {option, video, urlID} = location.state||{};
  
  const [isTranscribing, setIsTranscribing] = useState(false);

  function VideoPlayer({vid})
  {
   return (
    <div className=' shadow-[0px_3px_3px_black] rounded'> 
      <YouTube videoId={vid} opts={{height: '300', width: '500', playerVars: {autoplay: 1, mute: 1}}} className='rounded'/>
    </div>
  );
  }

  //Eshaan do this using handleTranscription function as reference
  function handleLipReading(e)
  {
    
  }

  //Melissa do this using handleTranscription function as reference
  function handleSubtitles()
  {
   
  }

  function handleTranscription(file)
  {
    setIsTranscribing(true);
    if(!file) {alert("Invalid file");return;}
    const formData = new FormData();
    
    //  Append media to form for media API
    if (file instanceof File) formData.append("video", file);  
    else if (typeof file === "string") formData.append("video_url_id", file);  
    else console.error("Invalid input");

    fetch('http://localhost:5000/videotranscribe',{method:'POST', body:formData})
   .then(res=>res.json())
   .then(data=>
   {
    setIsTranscribing(false);
    console.log("Transcript => ",data.transcript); 
    navigate('/transmedia',{state:{transcript:data.transcript,video,urlID}})
   })
   .catch((error)=>alert("Error:",error.error));
  }

  return (
    <div className='flex flex-col justify-center items-center w-screen h-screen gap-10'>
      {/* {video && <video src={video} controls autoPlay className='rounded w-[500px] shadow-[0px_3px_3px_black]'></video>} */}
      <div className='text-3xl'><h1>Transcription Options</h1></div>
      <div className='flex flex-col justify-center gap-5 w-[500px] p-5 rounded-2xl'>
        <button className='p-2 rounded-4xl  bg-blue-300 hover:bg-blue-200 active:bg-blue-500 cursor-pointer border-1 shadow-[0px_3px_5px_black] font-semibold' onClick={()=>handleLipReading()}>Lip Reading</button>
        {/* <button className='p-2 rounded-4xl  bg-purple-300 hover:bg-purple-200 active:bg-purple-500 cursor-pointer border-1 shadow-[0px_3px_5px_black] font-semibold' onClick={()=>handleSubtitles()}>Subtitles</button> */}
        <button className='p-2 rounded-4xl  bg-green-300 hover:bg-green-200 active:bg-green-500 cursor-pointer border-1 shadow-[0px_3px_5px_black] font-semibold' onClick={()=>handleTranscription(video ? video : urlID)}>Video Transcription</button>
      </div>

      {/* Transcribing */}
      {isTranscribing&&
      <div className='fixed flex justify-center items-center inset-20 bg-opacity-50 backdrop-blur-[3px] backdrop-brightness-50 rounded-2xl'>
        <h1 className='text-5xl text-white'>Transcribing.....</h1>
        {/* <img src={loader} alt="loader" /> */}
      </div>}
    </div>
  )
}