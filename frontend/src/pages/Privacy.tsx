import { useNavigate } from "react-router-dom";

export default function Privacy() {
    const navigate = useNavigate();
    return (
        <div style={{ maxWidth: "800px", margin: "0 auto", padding: "40px 20px", color: "var(--text-color)", overflowY: "auto", height: "100%", boxSizing: "border-box" }}>
            <h1 style={{ marginBottom: "2rem" }}>Privacy Policy</h1>

            <section style={{ marginBottom: "2rem" }}>
                <h2 style={{ fontSize: "1.3rem", borderBottom: "1px solid var(--border-color)", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
                    1. Data Storage & Local Indexing
                </h2>
                <p style={{ lineHeight: 1.6, opacity: 0.9 }}>
                    AI Mind Palace ("the Software") utilizes relational PostgreSQL databases to store your structured dashboard metadata (People, Projects, Decisions).
                    Additionally, conversations are processed and semantic memories are compiled into a localized FAISS Vector Database managed by the host.
                    Your embedded matrices are tightly bound to your authenticated `user_id`.
                </p>
            </section>

            <section style={{ marginBottom: "2rem" }}>
                <h2 style={{ fontSize: "1.3rem", borderBottom: "1px solid var(--border-color)", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
                    2. Third-Party LLM Endpoints
                </h2>
                <p style={{ lineHeight: 1.6, opacity: 0.9 }}>
                    Queries processed by the Software necessitate external network calls to Third-Party Large Language Model (LLM) providers (such as OpenAI, Google Gemini, or Groq) depending on the configuration. You acknowledge that your prompts and conversation buffers are transmitted securely over API protocols to these entities for natural language generation. Please review the respective privacy policies of these third-party providers regarding LLM data retention.
                </p>
            </section>

            <section style={{ marginBottom: "2rem" }}>
                <h2 style={{ fontSize: "1.3rem", borderBottom: "1px solid var(--border-color)", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
                    3. Authentication
                </h2>
                <p style={{ lineHeight: 1.6, opacity: 0.9 }}>
                    User authentication and session verification are securely handled via Clerk. We do not store or process your raw passwords. You can manage your access sessions explicitly through your Clerk profile portal.
                </p>
            </section>

            <section style={{ marginBottom: "2rem" }}>
                <h2 style={{ fontSize: "1.3rem", borderBottom: "1px solid var(--border-color)", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
                    4. Deletion Rights
                </h2>
                <p style={{ lineHeight: 1.6, opacity: 0.9 }}>
                    You possess explicit CRUD (Create, Read, Update, Delete) autonomy over all ingested metadata including dashboard variables, conversation logs, and generated FAISS memory embeddings directly through the application's user interface. Deleting a conversation, memory, or entity permanently erases it from the backend tables and vector index respectively.
                </p>
            </section>

            <div style={{ marginTop: "3rem", textAlign: "center" }}>
                <button onClick={() => navigate(-1)} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--subtext-color)", textDecoration: "none", opacity: 0.8, fontSize: "0.9rem", padding: 0 }}>&larr; Go Back</button>
            </div>
        </div>
    );
}
