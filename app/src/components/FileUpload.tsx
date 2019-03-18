import React, { Component, ChangeEvent } from 'react';
import axios from 'axios';
import '../App.css';

interface Props {}
interface State {
  selectedFile: File | null,
  fileValid: boolean,
  loaded: number;
}

class FileUpload extends Component<Props, State> {
    constructor(props: Props) {
      super(props);
      this.state = {
        selectedFile: null,
        loaded: 0,
        fileValid: false,
      };
  
      this.handleUpload = this.handleUpload.bind(this);
      this.handleSelectedFile = this.handleSelectedFile.bind(this);
    }
  
    handleSelectedFile(event: ChangeEvent<HTMLInputElement>) {
      if(event.target.files === null) {
        return;
      }
      const valid = event.target.files[0].name.slice(-4) === ".zip";
      this.setState({
        selectedFile: event.target.files[0],
        fileValid: valid
      });
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

    renderUpload() {
      if(this.state.selectedFile === null) {
        return (<div>Please select a file to upload</div>);
      }
      if(this.state.fileValid) {
        return (<button type='submit' onClick={this.handleUpload}>Upload</button>);
      } else {
        return (<div className="errorMsg">File is not valid, it must be a zip file.</div>);
      }
    }
  
    render() {
      return (
        <div className="App">
          <h1>Select a File to Upload</h1>
          <input type='file' name='firmware' onChange={this.handleSelectedFile} accept="application/zip" />
          <div className="container">
            {this.renderUpload()}
          </div>
          <div className="container">
            Uploaded: {this.state.loaded}
          </div>
        </div>
      );
    }
  }
  

  export default FileUpload;
  