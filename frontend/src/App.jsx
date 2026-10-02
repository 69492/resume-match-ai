import { useState } from "react";

export default function App() {
  const [apiStatus, setApiStatus] = useState("Not checked");
  async function checkApi() {
    try {
      const response = await fetch("/health");
      const data = await response.json();
      setApiStatus(data.status === "ok" ? "Connected" : "Unexpected response");
    } catch { setApiStatus("Unavailable"); }
  }
  return <main><h1>ResumeMatch AI</h1><p>Resume-to-job matching foundation.</p><button onClick={checkApi}>Check backend</button><p>Backend: {apiStatus}</p></main>;
}
