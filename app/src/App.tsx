import React, { Component, ChangeEvent } from 'react';
import axios from 'axios';
import './App.css';
import FileUpload from './components/FileUpload';



class App extends Component {
  
  render() {
    return (
      <div className="App">
        <FileUpload />
      </div>
    );
  }
}

export default App;
