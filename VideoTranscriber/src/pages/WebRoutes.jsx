import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

import Header from './Header'
import LoadingPage from './LoadingPage'
import LoginPage from './LoginPage'
import SigninPage from './SigninPage'
import HomePage from './HomePage'
import TranscriptionOptionPage from './TranscriptionOptionPage'
import MediaPage from './MediaPage'
import Questions from './Questions'
import UserAnalytics from './UserAnalytics'

export default function WebRoutes() {
  return (
    <div>
        {/* <Header/> */}
        <Router>
          <Routes>
            <Route path='/' element={<LoadingPage/>}/>
            <Route path='/login' element={<LoginPage/>}/>
            <Route path='/signin' element={<SigninPage/>}/>
            <Route path='/home' element={<HomePage/>}/>
            <Route path='/transoptions' element={<TranscriptionOptionPage/>}/>
            <Route path='/transmedia' element={<MediaPage/>}/>
            <Route path='/questionanswer' element={<Questions/>}/>
            <Route path='/userperformance' element={<UserAnalytics/>}/>
          </Routes>
        </Router>
    </div>
  )
}
