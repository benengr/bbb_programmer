import React, { Component, ChangeEvent } from 'react';
import axios from 'axios';
import './App.css';

interface Props {}
interface State {
  selectedFile: File | null,
  loaded: number;
}

class App extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      selectedFile: null,
      loaded: 0,
    };

    this.handleUpload = this.handleUpload.bind(this);
    this.handleSelectedFile = this.handleSelectedFile.bind(this);
  }

  handleSelectedFile(event: ChangeEvent<HTMLInputElement>) {
    if(event.target.files === null) {
      return;
    }
    this.setState({selectedFile: event.target.files[0]});
  }

  handleUpload(ignored: any) {
    if(this.state.selectedFile === null) {
      return;
    }
    const data = new FormData();
    data.append('firmware', this.state.selectedFile);
    
    axios.post('http://localhost:8080/api/v1/upload', data, {
      headers: {
        'content-type': 'multipart/form-data'
      },
      onUploadProgress: ProgressEvent => {
        this.setState({
          loaded: ProgressEvent.loaded / ProgressEvent.total * 100,
        })
      },
    }).then(res => {
      console.log(res.statusText);
    }).catch((error) => {
      alert(error);
    })
  }

  render() {
    return (
      <div className="App">
        <h1>Select a File to Upload</h1>
        <input type='file' name='firmware' onChange={this.handleSelectedFile} />
        <button type='submit' onClick={this.handleUpload}>Upload</button>
        
        
        <div>
          Uploaded: {this.state.loaded}
        </div>
      </div>
    );
  }
}

export default App;
