import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listNotes, createNote, uploadNote } from "../lib/api.js";
import { Link, useNavigate } from "react-router-dom";
import Uploader from "../components/Uploader.jsx";
import { useState } from "react";

export default function NotesList() {
  const nav = useNavigate();
  const qc = useQueryClient();

  const { data, error } = useQuery({ queryKey: ["notes"], queryFn: listNotes });
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");

  if (error && error.response && error.response.status === 401) {
    nav("/login");
  }

  const createMut = useMutation({
    mutationFn: () => createNote(title || "Untitled", text || ""),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notes"] });
      setTitle("");
      setText("");
    }
  });

  const uploadMut = useMutation({
    mutationFn: (f) => uploadNote(f, f.name),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notes"] })
  });

  return (
    <div>
      <div className="card">
        <h2>New Note</h2>
        <input placeholder="Title" value={title} onChange={e=>setTitle(e.target.value)} />
        <textarea placeholder="Write text..." rows={6} value={text} onChange={e=>setText(e.target.value)} />
        <button onClick={()=>createMut.mutate()}>Save</button>
      </div>

      <div className="card">
        <h2>Upload File</h2>
        <Uploader onFile={(f)=>uploadMut.mutate(f)} />
      </div>

      <h2>Your Notes</h2>
      <ul className="list">
        {data?.map(n => (
          <li key={n.id}><Link to={`/notes/${n.id}`}>{n.title}</Link></li>
        ))}
      </ul>
    </div>
  );
}
