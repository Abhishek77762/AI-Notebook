import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getNote,
  summarize,
  
  makePodcast,
  
  ragSearch,
  getAssetUrl,
  downloadAsset,
  updateNote
} from "../lib/api.js";
import { useState, useEffect } from "react";

export default function NoteDetail() {
  const { id } = useParams();
  const noteId = Number(id);
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ["note", noteId],
    queryFn: () => getNote(noteId)
  });

  // ----------------------------
  // EDIT MODE STATE
  // ----------------------------
  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editText, setEditText] = useState("");
  const [saveMsg, setSaveMsg] = useState("");

  useEffect(() => {
    if (data && !editing) {
      setEditTitle(data.title || "");
      setEditText(data.raw_text || "");
    }
  }, [data, editing]);

  const saveMut = useMutation({
    mutationFn: () => updateNote(noteId, { title: editTitle, raw_text: editText }),
    onSuccess: () => {
      setSaveMsg("Saved!");
      setEditing(false);
      qc.invalidateQueries({ queryKey: ["note", noteId] });
      // backend reindexes RAG automatically for this note
      setTimeout(() => setSaveMsg(""), 1500);
    },
    onError: (e) => {
      setSaveMsg(e?.response?.data?.detail || "Save failed");
    }
  });

  // ----------------------------
  // SUMMARY STATE
  // ----------------------------
  const [summary, setSummary] = useState("");
  const pointsMut = useMutation({
    mutationFn: () => summarize(noteId, "points"),
    onSuccess: setSummary
  });
  const parasMut = useMutation({
    mutationFn: () => summarize(noteId, "paragraphs"),
    onSuccess: setSummary
  });

  // ----------------------------
  // PODCAST UI STATE + HANDLER
  // ----------------------------
  const [podcastUrl, setPodcastUrl] = useState("");
  const [assetId, setAssetId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const podcastMut = useMutation({
    mutationFn: async () => {
      setIsLoading(true);
      setError(null);
      try {
        const result = await makePodcast(noteId);
        return result;
      } finally {
        setIsLoading(false);
      }
    },
    onSuccess: async (res) => {
      if (res && res.asset_id) {
        setAssetId(res.asset_id);
        try {
          const audioBlob = await downloadAsset(res.asset_id);
          const audioUrl = URL.createObjectURL(audioBlob);
          setPodcastUrl(audioUrl);
        } catch (err) {
          console.error("Error loading audio:", err);
          setError("Failed to load audio. Please try again.");
        }
      }
    },
    onError: (error) => {
      console.error("Podcast creation failed:", error);
      setError("Failed to create podcast. " + (error.message || ""));
    }
  });

  const handleDownload = async () => {
    try {
      const blob = await downloadAsset(assetId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `podcast_${assetId}.mp3`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (error) {
      console.error("Download failed:", error);
    }
  };

  

  // ----------------------------
  // RAG
  // ----------------------------
  const [ragQ, setRagQ] = useState("");
  const [ragAns, setRagAns] = useState("");
  const [ragHits, setRagHits] = useState([]);

  const ragMut = useMutation({
    mutationFn: () => ragSearch(ragQ, 5),
    onSuccess: (res) => {
      setRagAns(res.answer);
      setRagHits(res.hits || []);
    }
  });

  if (!data) return <p>Loading...</p>;

  const preview = data.raw_text?.slice(0, 800) || "";

  return (
    <div>
      {/* ----------------------------
          VIEW vs EDIT HEADER
         ---------------------------- */}
      {!editing ? (
        <>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <h2 style={{ margin: 0 }}>{data.title}</h2>
            <button onClick={() => setEditing(true)}>Edit</button>
            {saveMsg && <span style={{ color: saveMut.isError ? "crimson" : "#059669" }}>{saveMsg}</span>}
          </div>
          <pre className="note">
            {preview}
            {data.raw_text && data.raw_text.length > 800 ? " ..." : ""}
          </pre>
        </>
      ) : (
        <div className="card">
          <h3>Edit Note</h3>
          <input
            placeholder="Title"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
          />
          <textarea
            placeholder="Write text..."
            rows={12}
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
          />
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={() => saveMut.mutate()}>Save</button>
            <button
              onClick={() => {
                setEditing(false);
                setEditTitle(data.title || "");
                setEditText(data.raw_text || "");
                setSaveMsg("");
              }}
            >
              Cancel
            </button>
          </div>
          {saveMsg && (
            <p style={{ color: saveMut.isError ? "crimson" : "#059669" }}>
              {saveMsg}
            </p>
          )}
        </div>
      )}

      <div className="card">
        <h3>AI Actions</h3>
        <button onClick={() => pointsMut.mutate()}>Summarize → Points</button>
        <button onClick={() => parasMut.mutate()}>Summarize → Paragraphs</button>
        
        <button onClick={() => podcastMut.mutate()}>Create Podcast (MP3)</button>
        
      </div>

      {summary && (
        <div className="card">
          <h4>Summary</h4>
          <pre className="summary">{summary}</pre>
        </div>
      )}

      

      {/* ----------------------------
          PODCAST PLAYER
         ---------------------------- */}
      {(podcastUrl || isLoading) && (
        <div className="card">
          <h4>Podcast</h4>
          {isLoading ? (
            <p>Creating podcast... This may take a moment.</p>
          ) : error ? (
            <p className="error">{error}</p>
          ) : (
            <>
              <audio
                controls
                src={podcastUrl}
                style={{ width: "100%" }}
                onError={(e) => {
                  console.error("Audio playback error:", e);
                  setError("Failed to play audio. The file might be corrupted.");
                }}
              />
              <button
                onClick={handleDownload}
                style={{ marginTop: "10px" }}
                disabled={!podcastUrl}
              >
                Download MP3
              </button>
            </>
          )}
        </div>
      )}

      <div className="card">
        <h3>Search across your notes (RAG)</h3>
        <input
          placeholder="Ask a question..."
          value={ragQ}
          onChange={(e) => setRagQ(e.target.value)}
        />
        <button onClick={() => ragMut.mutate()}>Ask</button>

        {ragAns && (
          <>
            <h4>Answer</h4>
            <pre className="summary">{ragAns}</pre>
          </>
        )}

        {ragHits?.length ? (
          <>
            <h4>Sources</h4>
            <ul>
              {ragHits.map((h, i) => (
                <li key={i}>
                  note {h.note_id} / chunk {h.idx} — score{" "}
                  {Number(h.score || 0).toFixed(3)}
                  <div style={{ fontSize: 12, opacity: 0.8 }}>
                    {(h.text || "").slice(0, 220)}
                    {(h.text || "").length > 220 ? "..." : ""}
                  </div>
                </li>
              ))}
            </ul>
          </>
        ) : null}
      </div>
    </div>
  );
}
