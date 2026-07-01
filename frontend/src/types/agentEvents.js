/*
AgentOS SSE event shapes.

These are the 9 event types the backend will stream later:

1. session_start
{
  type: "session_start",
  session_id: "...",
  domain: "...",
  query: "...",
  ts: 1234567890
}

2. planner_done
{
  type: "planner_done",
  agent: "planner",
  subtasks: ["...", "..."],
  ts: 1234567890
}

3. memory_read
{
  type: "memory_read",
  agent: "planner" | "researcher" | "writer",
  dataset: "u_demo_d_ai_safety",
  ts: 1234567890
}

4. memory_write
{
  type: "memory_write",
  agent: "researcher",
  dataset: "u_demo_d_ai_safety",
  preview: "Short text preview...",
  ts: 1234567890
}

5. researcher_finding
{
  type: "researcher_finding",
  agent: "researcher",
  subtask: "...",
  text: "...",
  ts: 1234567890
}

6. writer_answer
{
  type: "writer_answer",
  agent: "writer",
  grounded: true,
  text: "...",
  citations: [],
  ts: 1234567890
}

7. graph_updated
{
  type: "graph_updated",
  node_count: 10,
  edge_count: 8,
  ts: 1234567890
}

8. session_complete
{
  type: "session_complete",
  session_id: "...",
  ts: 1234567890
}

9. session_error
{
  type: "session_error",
  session_id: "...",
  error: "...",
  ts: 1234567890
}
*/

export const AGENT_EVENT_TYPES = [
  "session_start",
  "planner_done",
  "memory_read",
  "memory_write",
  "researcher_finding",
  "writer_answer",
  "graph_updated",
  "session_complete",
  "session_error",
]