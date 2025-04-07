import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

const data = [
  { name: "Fill in the Blanks", score: 4, total: 5 },
  { name: "MCQ", score: 3, total: 5 },
  { name: "Multiple Blanks", score: 2, total: 5 },
];

const COLORS = ["#33ff57", "#fff333", "#ff3333"];

const getMessage = (percentage) => {
  if (percentage >= 80) return "Well done!";
  if (percentage >= 50) return "Keep going!";
  return "Better luck next time!";
};

export default function Statistics() {
  return (
    <div style={{ textAlign: "center" }}>
      <h2>Quiz Performance</h2>
      {data.map((item, index) => {
        const percentage = (item.score / item.total) * 100;
        const chartData = [
          { name: "Correct", value: item.score },
          { name: "Incorrect", value: item.total - item.score },
        ];

        return (
         <div>
             <div className="flex flex-col justify-center items-center" key={index} style={{ marginBottom: "40px" }}>
               <h3>{item.name}</h3>
               <PieChart width={300} height={300}>
                 <Pie
                   data={chartData}
                   dataKey="value"
                   cx="50%"
                   cy="50%"
                   innerRadius={60}
                   outerRadius={100}
                   fill="#8884d8"
                   paddingAngle={5}
                   label={({ percent }) => {'${(percent * 100).toFixed(0)}%'}}
                 >
                   {chartData.map((entry, i) => (
                     <Cell key={i} fill={i === 0 ? COLORS[0] : COLORS[2]} />
                   ))}
                 </Pie>
                 <Tooltip />
                 <Legend />
               </PieChart>
               <p><strong>{item.score}/{item.total}</strong></p>
               <p>{getMessage(percentage)}</p>
             </div>
         </div>
        );
      })}
    </div>
  );
}