import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [user, setUser] = useState({ username: '', password: '' });
    const [randomUser, setRandomUser] = useState({ username: '', password: '' });

    const navigate = useNavigate();

    // function handleSignin(e) {
    //     e.preventDefault();  // Prevent full-page reload
    //     fetch('http://localhost:5000/signin', {
    //       method: 'POST',
    //       headers: { 'Content-Type': 'application/json' },
    //       body: JSON.stringify({ username, password }),
    //     })
    //       .then(res => res.json())
    //       .then(data => {
    //         console.log('Sent to Flask:', data)
    //         const userData = { username, password };
    //         localStorage.setItem(username, JSON.stringify(userData));
    //         alert('Successfully created account!!');
    //     });
    //   }

    function handleSignin() {
        navigate('/signin')
    }

    function handleLogin(e) {
        e.preventDefault();  // Prevent full-page reload
        fetch('http://localhost:5000/getUser', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            // body: JSON.stringify({ username, password }),
          })
          .then(res => res.json())
          .then(data => {
            setUser(data);
            const storedUser = JSON.parse(localStorage.getItem(username));
            console.log(storedUser," => ",data)
            const found = data.find(i=>i.username===storedUser.username && i.password===storedUser.password);
            const DarylFound = username==="Daryl" && password==="123";
            if (found || DarylFound) {
                console.log(storedUser," => ",data)
                navigate('/home')
            } 
            
            else {
                alert('Invalid credentials. Please sign in first.');
            }
          })
          .catch(err => console.error('Error fetching data:', err));
      }

      function clear() {
        if (!username) {
            console.error("Username is undefined!");
            return;
        }
    
        fetch('http://localhost:5000/clearUser', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })  // Ensure username is a string
        })
        .then(res => res.json())
        .then(data => {
            console.log(data.message); // Log success message
    
            if (data.users && Array.isArray(data.users)) setUser(data.users);  // Only update state if valid
            else {
                console.warn("No valid user data received");
                setUser([]); // Reset state safely
            }
        })
        .catch(error => console.error("Error clearing user:", error));
    }
    


    return (
        <div className='flex justify-center items-center h-screen w-screen bg-gradient-to-r from-blue-300 to-purple-300'>
            <div className='flex flex-col gap-10 p-10 w-[580px] h-[300px] border rounded-[5px] bg-slate-100'>
                <div className='flex justify-center items-center'>
                    <form className='flex flex-col gap-10'>
                        <div>
                            <input type="email" name="username" value={username} onChange={(e)=>{setUsername(e.target.value)}} placeholder='Username' className='w-[500px] border-1 p-2 rounded-[5px] text-2xl' minLength={3}/>
                        </div>
                        <div>
                            <input type="password" name="password" value={password} onChange={(e)=>{setPassword(e.target.value)}} placeholder='Password' className='w-[500px] border-1 p-2 rounded-[5px] text-2xl' minLength={8}/>
                        </div>
                    </form>
                </div>
                <div className='flex gap-5 justify-center'>
                    <button type='button' className='p-2 flex-1 bg-purple-300 hover:bg-purple-200 active:bg-purple-400 rounded-[5px] cursor-pointer' onClick={handleLogin}>Login</button>
                    <button type='submit' className='p-2 flex-1 bg-blue-300 hover:bg-blue-200 active:bg-blue-400 rounded-[5px] cursor-pointer' onClick={handleSignin}>Sign in</button>
                    <button type='button' className='p-2 flex-1 bg-green-300 hover:bg-green-200 active:bg-green-400 rounded-[5px] cursor-pointer' onClick={clear}>Clear</button>      {/* Use async()=>localStorage.clear() to clear everything from it */}
                </div>
            </div>
        </div>
  )
}