import React, { useState } from 'react';

export default function Mongo() {
  const [users, setUsers] = useState([]);

  // Add user
  const addUser = async () => {
    const response = await fetch('http://localhost:5000/addUser', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'Daryl', password: '123' }),
    });
    if (response.ok) {
      alert('User added!');
    } else {
      alert('Failed to add user');
    }
  };

  // Get users
  const getUsers = async () => {
    const response = await fetch('http://localhost:5000/users');
    const data = await response.json();
    setUsers(data);
  };

  return (
    <div>
      <button onClick={addUser} className="bg-red-500 p-2 m-2">Add User</button>
      <button onClick={getUsers} className="bg-green-500 p-2 m-2">Show Users</button>
      <ul>
        {users.map((user, index) => (
          <li key={index}>{user.username}</li>
        ))}
      </ul>
    </div>
  );
}
