import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom';
import YouTube from 'react-youtube';

export default function HomePage() {

  const [option, setOption] = useState(""); // Store selected option
  const [file, setFile] = useState(null);
  const [video, setVideo] = useState(null);
  // const [url, setUrl] = useState("");
  const [urlID, setUrlID] = useState("");

  const navigate = useNavigate();

  function extractYouTubeID(url) {
    const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:.*v=|.*\/)([^&?]*))/);
    // if(match) setUrlID(match);
    return match ? match[1] : null;
  }

  function handleUpload(file) {
    if(!file) console.log("No file or URL provided");
    else{

      if (file instanceof File) setVideo(file);   //If video file
      else if (typeof file === "string") setUrlID(extractYouTubeID(file))  //If url
      else console.error("Invalid input");
    }
  }

  function VideoPlayer({vid})
  {
   return (
    <div className=' shadow-[0px_3px_3px_black] rounded'> 
      <YouTube videoId={vid} opts={{height: '300', width: '500', playerVars: {autoplay: 1, mute: 1}}} className='rounded'/>
    </div>
  );
  }

  return (
    <div className='flex justify-center items-center h-screen w-screen bg-gradient-to-r from-blue-300 to-purple-300'>
      <div className='flex flex-col justify-start border rounded bg-slate-200 w-[700px] h-[500px] gap-8 p-8 relative'>

        {/* Upload Options */}
        <div>
          <select className='border p-2 rounded bg-white' value={option} onChange={(e)=>setOption(e.target.value)}>
            <option value="">Select option</option>
            <option value="video">Upload video</option>
            <option value="url">Upload url</option>
          </select>
        </div>

        {/* Input field */}
        <div className='flex gap-5'>
          {/* video */}
          {option==="video"&&(<input type="file" accept="video/*" className='border p-2 w-[500px] rounded bg-white' onChange={(e)=>handleUpload(e.target.files[0])}/>)}
          
          {/* url */}
          {option==="url"&&(<input type="text" placeholder='Enter URL' className='border p-2 rounded flex-1 font-semibold bg-white' onChange={(e)=>handleUpload(e.target.value)}/>)}
          
          {/* Submit/Transcribe button */}
          {option&&(<button className='bg-blue-400 hover:bg-blue-300 active:bg-blue-500 p-2 flex-1 rounded border cursor-pointer' onClick={()=>{(video||urlID) ? navigate('/transoptions',{state:{option,video,urlID}}) : alert('Invalid video or URL') }}>Transcribe</button>)}
        </div>
        <div className='absolute top-[180px] rounded'>
          {(video) && <video src={URL.createObjectURL(video)} controls autoPlay className='rounded w-[500px] shadow-[0px_3px_3px_black]'></video>}

          {(urlID) && <VideoPlayer vid={urlID}/>} {/* https://www.youtube.com/watch?v=XUGyuG4L2uM */}

        </div>
      </div>
    </div>
  )
}
