import React from 'react';
import logo from './logo.svg';
import './App.css';
import Game from './game/Game';

const playerNames = ["Alex", "Ben", "Carl", "David", "Eddy", "Fred", "Geroge"]

function App() {
  return (
    <div className="App">
      <Game names={playerNames} />
    </div>
  );
}

export default App;
