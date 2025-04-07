// import React, { useEffect, useState } from 'react'
// import { useLocation, useNavigate } from 'react-router-dom'

// export default function Questions() {

//     const navigate = useNavigate();
    // const location = useLocation();
    // const {summary, keywords} = location.state||{};

//     const [option, setOption] = useState(0);
//     const [numQuestions, setNumQuestions] = useState(0);
//     const [showQuestions, setShowQuestions]=useState(false);
//     const [questions, setQuestions] = useState(null);
//     const [answers, setAnswers] = useState(null);
//     const [answer, setAnswer] = useState(null);

//     useEffect(()=>
//     {
//      getQuestions(option)
//     },[option])

//     useEffect(()=>
//     {
//      if(questions) setShowQuestions(true)
//      console.log("Questions=", questions)
//      console.log(showQuestions)
//     },[questions])

//     function getQuestions(optionValue)
//     {
//       fetch("http://localhost:5000/showQuestions",{method:'POST',
//                                                    headers: { 'Content-Type': 'application/json' }, 
//                                                    body: JSON.stringify({summary, keywords:keywords.map(item=>item[0]), optionValue, numQuestions})})   //item[0] for words only instead of counts
//       .then(res=>res.json())
//       .then(data=>
//       {
//         console.log("data=", data,"\nQuestionsData", data.questions)
//         setQuestions(data.questions);
//         setAnswers(data.answers);
//       })
//     }
//     return (
//     <div>
//         <div>Question Page</div>

//         <div className='flex gap-5'>
//           <label>How many questions</label>
//           <input type="number" value={numQuestions} onChange={(e)=>setNumQuestions(e.target.value)} min={1} max={10} className="border rounded w-10"/>
//         </div>

//         {/* Upload Options */}
//         <div>
//           <select className='border p-2 rounded bg-white' value={option} onChange={(e)=>setOption(e.target.value)}>
//             <option value="0">Select option</option>
//             <option value="1">Fill in the blanks</option>
//             <option value="2">Multiple Choice Questions</option>
//             <option value="3">Multiple Blank Questions</option>
//           </select>
//         </div>

//         {showQuestions&&
//         <div>
//         {
//          questions.map((Q,index)=>
//          (
//           <div key={index}>
//             <h2>{index+1}) {Q}</h2>
//             <input type="text" value={answer} onChange={(e)=>setAnswer(e.target.value)}/>
//             <button className='bg-blue-400 p-2 cursor-pointer' onClick={SubmitAnswer}>Submit Answer</button>
//           </div>
//          ))
//         }
//         </div>
//         }

//     </div>
//   )
// }

import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function Questions() {

const navigate = useNavigate();
const location = useLocation();

const summary="supervised and unsupervised learning..."
const keywords=[]
const [option, setOption] = useState("0");
const [numQuestions, setNumQuestions] = useState(0);
const [showQuestions, setShowQuestions]=useState(false);
const [questions, setQuestions] = useState([]);
const [answers, setAnswers] = useState([]);
const [submitted, setSubmitted] = useState(false);
const [results, setResults] = useState([]);

const fillQuestions=[
  {question: "supervised learning is when we train the model with labeled data. We tell the model this is what the right output should be based on this __________.", answer: "info"},
  {question: "each has its place and choosing the right one depends on the __________ that you are trying to solve.", answer: "problem"}
]

const mcqQuestions=[
  {question: "supervised learning is when we train the __________ with labeled data.", options: ["cart","data","model","problem"], answer: "model"},
  {question: "choosing the right one depends on the __________.", options: ["data","model","group","goal"], answer: "goal"}
]

const mbQuestions=[
  {question: "supervised learning is when we train the model with labeled __________... it would be able to predict that __________ customers who buy peanut butter might also...", answers: ["data", "future"]},
  {question: "supervised learning is when we train the __________ with labeled data... one depends on the __________ you're trying to solve...", answers: ["model", "problem"]}
]

useEffect(()=>{
  setShowQuestions(false)
  setAnswers([])
  setResults([])
  setSubmitted(false)
  if(option==="1") {
    setQuestions(fillQuestions)
    setAnswers(new Array(fillQuestions.length).fill(""))
    setResults(new Array(fillQuestions.length).fill(""))
  } else if(option==="2") {
    setQuestions(mcqQuestions)
    setAnswers(new Array(mcqQuestions.length).fill(""))
    setResults(new Array(mcqQuestions.length).fill(""))
  } else if(option==="3") {
    setQuestions(mbQuestions)
    setAnswers(mbQuestions.map(q=>new Array(q.answers.length).fill("")))
    setResults(mbQuestions.map(q=>new Array(q.answers.length).fill("")))
  }
  setNumQuestions(option==="1"?fillQuestions.length:option==="2"?mcqQuestions.length:mbQuestions.length)
  setShowQuestions(true)
},[option])

const handleFbChange = (index, value) => {
  const updated = [...answers]
  updated[index] = value
  setAnswers(updated)
}

const handleMcqChange = (index, value) => {
  const updated = [...answers]
  updated[index] = value
  setAnswers(updated)
}

const handleMbChange = (qIdx, aIdx, value) => {
  const updated = [...answers]
  updated[qIdx][aIdx] = value
  setAnswers(updated)
}

const SubmitAnswer = () => {
  let evals=[]
  if(option==="1") {
    evals = answers.map((ans,i)=>{
      if(ans.trim().toLowerCase() === fillQuestions[i].answer.toLowerCase()) {
        return "Correct answer"
      } else {
        return `Wrong answer. Correct answer: ${fillQuestions[i].answer}`
      }
    })
  }
  else if(option==="2") {
    evals = answers.map((ans,i)=>{
      const correct = mcqQuestions[i].answer.toLowerCase()
      const selected = ans.trim().toLowerCase()
      if(selected === correct) {
        return "Correct answer"
      } else {
        return `Wrong answer. Correct answer: ${mcqQuestions[i].answer}`
      }
    })
  }
  else if(option==="3") {
    evals = answers.map((group,i)=>{
      return group.map((ans,j)=>{
        if(ans.trim().toLowerCase() === mbQuestions[i].answers[j].toLowerCase()) {
          return "Correct answer"
        } else {
          return `Wrong answer. Correct answer: ${mbQuestions[i].answers[j]}`
        }
      })
    })
  }
  setResults(evals)
  setSubmitted(true)
}

return (
<div>
<div>Question Page</div>

<div className='flex gap-5'>
    <label>How many questions</label>
    <input type="number" value={numQuestions} onChange={(e)=>setNumQuestions(e.target.value)} min={1} max={10} className="border rounded w-10"/>
</div>

<div>
    <select className='border p-2 rounded bg-white' value={option} onChange={(e)=>setOption(e.target.value)}>
    <option value="0">Select option</option>
    <option value="1">Fill in the blanks</option>
    <option value="2">Multiple Choice Questions</option>
    <option value="3">Multiple Blank Questions</option>
</select>
</div>

{showQuestions && option==="1" && questions.map((q,i)=>(
    <div key={i}>
        <p>{i+1}) {q.question}</p>
        <input type="text" value={answers[i]} onChange={(e)=>handleFbChange(i,e.target.value)} />
        {submitted && <p>{results[i]}</p>}
        </div>
))}

{showQuestions && option==="2" && questions.map((q,i)=>(
<div key={i}>
    <p>{i+1}) {q.question}</p>
{
 q.options.map((opt, j)=>
 (
    <div key={j}>
    <input type="radio" name={`mcq-${i}`} value={opt} checked={answers[i]===opt} onChange={(e)=>handleMcqChange(i,opt)} />
    <label>{opt}</label>
    </div>
 ))
}
    {submitted && <p>{results[i]}</p>}
</div>
))}

{showQuestions && option==="3" && questions.map((q,i)=>(
<div key={i}>
    <p>{i+1}) {q.question}</p>
    {Array.isArray(q.answers) && q.answers.map((_,j)=>(
<div key={j}>
    <input type="text" placeholder={`Answer ${j+1}`} value={answers[i][j]} onChange={(e)=>handleMbChange(i,j,e.target.value)} />
    {submitted && <p>{results[i][j]}</p>}
</div>
))}
</div>
))}

{showQuestions && <button className='bg-blue-400 p-2 cursor-pointer' onClick={SubmitAnswer}>Submit All Answers</button>}

</div>
)
}