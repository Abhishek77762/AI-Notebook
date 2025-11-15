import axios from "axios";

export const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem("token");
  if (token) {
    cfg.headers = cfg.headers || {};
    cfg.headers.Authorization = `Bearer ${token}`;
  }
  return cfg;
});

export async function updateNote(id, fields /* {title?, raw_text?, html?} */) {
  const { data } = await api.put(`/notes/${id}`, fields);
  return data; // NoteOut
}
export async function listNotes() {
  const { data } = await api.get("/notes");
  return data;
}
export async function getNote(id) {
  const { data } = await api.get(`/notes/${id}`);
  return data;
}
export async function createNote(title, raw_text, html) {
  const { data } = await api.post("/notes", { title, raw_text, html });
  return data;
}
export async function uploadNote(file, title) {
  const form = new FormData();
  form.append("file", file);
  form.append("title", title);
  const { data } = await api.post("/notes/upload", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
}


export async function summarize(note_id, style /* "points"|"paragraphs" */) {
  const { data } = await api.post("/ai/summarize", { note_id, style });
  return data.summary;
}

export async function ragSearch(query, top_k = 5) {
  const { data } = await api.post("/ai/search", { query, top_k });
  return data;
}
export async function makePodcast(note_id) {
  const { data } = await api.post("/ai/podcast", { note_id });
  return data; 
}

export async function getAssetUrl(asset_id) {
  return `/api/assets/${asset_id}`; // The actual URL for the asset
}

export async function downloadAsset(asset_id) {
  const response = await api.get(`/assets/${asset_id}`, { 
    responseType: 'blob' 
  });
  return response.data;
}


export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return data; 
}
export async function register(email, password) {
  const { data } = await api.post("/auth/register", { email, password });
  return data; 
}
export async function googleAuth(id_token) {
  const { data } = await api.post("/auth/google", { id_token });
  return data; 
}
export async function me() {
  const { data } = await api.get("/auth/me");
  return data; 
}
