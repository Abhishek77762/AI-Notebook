import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";

export default function Editor({ value, onChange }) {
  return <ReactQuill theme="snow" value={value} onChange={onChange} />;
}
