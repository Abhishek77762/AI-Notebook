import { useCallback} from "react"
import { useDropzone } from "react-dropzone";


export default function Uploader({onFile}){
    const onDrop = useCallback((accepted)=>{
        if(accepted && accepted.length) onFile(accepted[0]);
    },[onFile]);


const {getRootProps, getInputProps, isDragActive} = useDropzone({onDrop});


    return (
    <div className="uploader" {...getRootProps()}>
      <input {...getInputProps()} />
      {isDragActive
        ? <p>Drop the file here ...</p>
        : <p>Drag & drop PDF/DOCX/TXT here, or click to select.</p>}
    </div>
  );

}




