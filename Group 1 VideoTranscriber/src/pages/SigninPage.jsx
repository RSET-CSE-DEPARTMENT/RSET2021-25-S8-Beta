import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';

export default function SigninPage() {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const navigate = useNavigate();

    function handleSignin(e) {
        e.preventDefault();  // Prevent full-page reload
        fetch('http://localhost:5000/signin', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        })
          .then(res => res.json())
          .then(data => {
            console.log('Sent to Flask:', data)
            const userData = { username, password };
            localStorage.setItem(username, JSON.stringify(userData));
            alert('Successfully created account!!');
            navigate('/login');
        });
      }

    return (
        <div className='flex justify-center items-center h-screen w-screen bg-gradient-to-r from-blue-300 to-purple-300'>
            <div className='flex flex-col gap-10 p-10 w-[580px] h-[300px] border rounded-[5px] bg-slate-100'>
                <div className='flex justify-center items-center'>
                    <form className='flex flex-col gap-10'>
                        <div>
                            <input type="email" name="username" value={username} onChange={(e)=>{setUsername(e.target.value)}} placeholder='Username' className='w-[500px] border-1 p-2 rounded-[5px] text-2xl' minLength="3" required/>
                        </div>
                        <div>
                            <input type="password" name="password" value={password} onChange={(e)=>{setPassword(e.target.value)}} placeholder='Password' className='w-[500px] border-1 p-2 rounded-[5px] text-2xl' minLength="8"/>
                        </div>
                        <div className='flex gap-5 justify-center'>
                            <button type='submit' className='p-2 flex-1 bg-blue-300 hover:bg-blue-200 active:bg-blue-400 rounded-[5px] cursor-pointer' onClick={handleSignin}>Sign in</button>
                        </div>
                    </form>
                </div>
                
            </div>
        </div>
  )
}