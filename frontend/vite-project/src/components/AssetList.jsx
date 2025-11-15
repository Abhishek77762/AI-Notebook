import { assetUrl } from "../lib/api";

export default function AssetList({ assets }) {
  if (!assets || !assets.length) return null;
  return (
    <div className="card">
      <h3>Assets</h3>
      <ul>
        {assets.map(a => (
          <li key={a.id}>
            <a href={assetUrl(a.id)} target="_blank" rel="noreferrer">
              {a.kind} (#{a.id})
            </a>
            <small> — {new Date(a.created_at).toLocaleString()}</small>
          </li>
        ))}
      </ul>
    </div>
  );
}
