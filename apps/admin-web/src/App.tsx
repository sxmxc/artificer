import { Link, Route, Routes } from "react-router-dom";

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <h1>Cuddly Octo Memory</h1>
          <p className="subtitle">Mock API platform</p>
        </div>
      </header>
      <main className="page">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  );
}

function Home() {
  return (
    <div>
      <h2>Welcome</h2>
      <p>
        This is the admin dashboard placeholder. Build endpoint management pages in <code>src/</code>.
      </p>
      <p>
        API is expected at <code>/api/</code>. Try <code>/api/admin/endpoints</code>.
      </p>
      <p>
        <Link to="/endpoints">Go to endpoints</Link> (not implemented yet)
      </p>
    </div>
  );
}

function NotFound() {
  return (
    <div>
      <h2>Not found</h2>
      <p>
        <Link to="/">Back home</Link>
      </p>
    </div>
  );
}
