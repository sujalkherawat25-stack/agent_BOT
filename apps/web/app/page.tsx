"use client";
import {FormEvent, useState} from "react";

type Item = {role: "user" | "assistant"; text: string};
const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [items, setItems] = useState<Item[]>([{role: "assistant", text: "What would you like to get done?"}]);
  const [message, setMessage] = useState("");
  const [activity, setActivity] = useState("Ready");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); if (!message.trim() || busy) return;
    const outgoing = message; setMessage(""); setBusy(true); setItems(old => [...old, {role: "user", text: outgoing}]);
    try {
      const response = await fetch(`${api}/v1/chat/messages`, {method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({message: outgoing, timezone: Intl.DateTimeFormat().resolvedOptions().timeZone})});
      if (!response.body) throw new Error("No response stream");
      const reader = response.body.getReader(), decoder = new TextDecoder(); let pending = "", answer = "";
      while (true) { const {done, value} = await reader.read(); if (done) break; pending += decoder.decode(value, {stream:true}); const blocks = pending.split("\n\n"); pending = blocks.pop() || ""; for (const block of blocks) { const data = block.split("\n").find(line => line.startsWith("data: "))?.slice(6); if (!data) continue; const event = JSON.parse(data); if (event.type === "token") answer += event.payload.text; if (event.payload.label) setActivity(event.payload.label); } }
      setItems(old => [...old, {role: "assistant", text: answer || "Done."}]); setActivity("Completed");
    } catch (error) { setItems(old => [...old, {role:"assistant", text:"I couldn’t complete that request. Please try again."}]); setActivity("Failed"); }
    finally { setBusy(false); }
  }
  return <main><aside><div className="brand">Memento<span>●</span></div><nav><a className="active">Chat</a><a>Tasks</a><a>Research</a><a>Memory</a><a>Settings</a></nav></aside><section><header><div><p className="eyebrow">PERSONAL AGENT</p><h1>Good afternoon</h1></div><div className="activity" aria-live="polite"><i/> {activity}</div></header><div className="messages">{items.map((item, index) => <article className={item.role} key={index}>{item.text}</article>)}</div><form onSubmit={submit}><input value={message} onChange={e=>setMessage(e.target.value)} placeholder="Ask anything, or create a reminder…" aria-label="Message"/><button disabled={busy}>{busy ? "Working" : "Send"}</button></form><p className="hint">Try “Remind me tomorrow at 9 AM to send the report.”</p></section><aside className="context"><p className="eyebrow">CONTEXT</p><h2>Today</h2><p>Your agent will show sources, tasks, and activity here when they matter.</p></aside></main>;
}
