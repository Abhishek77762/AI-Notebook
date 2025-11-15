import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import App from "./App.jsx";
import NotesList from "./pages/NotesList.jsx";
import NoteDetail from "./pages/NoteDetail.jsx";
import Login from "./pages/Login.jsx";

const qc = new QueryClient();

createRoot(document.getElementById("root")).render(
   <React.StrictMode>
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route index element={<NotesList />} />
            <Route path="login" element={<Login />} />
            <Route path="notes/:id" element={<NoteDetail />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
