import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import vtlogo from '../assets/videotranscriberlogo.jpg'

export default function LoadingPage() {

  const [progressValue, setProgressValue] = useState(0);
  const navigate = useNavigate();

  useEffect(()=>{
    if(progressValue<=100) {
      const timer = setTimeout(()=>{
        setProgressValue(prev=>prev+20);
        console.log(progressValue);
      },1000)
  
      return ()=>clearTimeout(timer);
    }
    else navigate('/login');
  },[progressValue])

  return (
    <div className='flex flex-col items-center gap-24 mt-28'>
        <div className='flex justify-center items-center'>
            <img src={vtlogo} alt="VT Logo" className='w-[250px] h-[250px] rounded-[80px]'/>
        </div>
        <div className='flex gap-3 items-center'>
            <div className='flex  gap-3 h-[50px] w-[500px] border-1 border-black rounded-2xl'>
                <div className="h-[48px] bg-green-500 rounded-2xl" style={{width:`${progressValue*5}px`, transition: "width 300ms ease-in-out"}}></div>
            </div>
            <h1 className='font-bold'>{progressValue}%</h1>
        </div>
    </div>
  )
}
