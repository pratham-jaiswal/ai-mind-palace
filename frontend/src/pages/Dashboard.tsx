import { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '@clerk/clerk-react';
import { PuffLoader } from 'react-spinners';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function Dashboard() {
  const { getToken } = useAuth();
  const [people, setPeople] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [decisions, setDecisions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal State
  const [modalType, setModalType] = useState<"person" | "project" | "decision" | null>(null);
  const [modalMode, setModalMode] = useState<"add" | "edit">("add");
  const [editingId, setEditingId] = useState<number | null>(null);

  // Form State
  const [formData, setFormData] = useState<any>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchData();
  }, [getToken]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = await getToken();
      const headers = { Authorization: `Bearer ${token}` };

      const [resPeople, resProjects, resDecisions] = await Promise.all([
        axios.get(`${BACKEND_URL}/people/`, { headers }),
        axios.get(`${BACKEND_URL}/projects/`, { headers }),
        axios.get(`${BACKEND_URL}/decisions/`, { headers })
      ]);

      const fetchedPeople = resPeople.data.result || [];
      fetchedPeople.sort((a: any, b: any) => {
        const aName = (a.name || "").toLowerCase();
        const bName = (b.name || "").toLowerCase();
        const isASelf = aName === "self" || aName === "me";
        const isBSelf = bName === "self" || bName === "me";
        if (isASelf && !isBSelf) return -1;
        if (!isASelf && isBSelf) return 1;
        return aName.localeCompare(bName);
      });

      setPeople(fetchedPeople);
      setProjects(resProjects.data.result || []);

      const fetchedDecisions = resDecisions.data.result || [];
      fetchedDecisions.sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime());
      setDecisions(fetchedDecisions);
    } catch (err) {
      console.error("Error fetching dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  const openModal = (type: "person" | "project" | "decision", mode: "add" | "edit", initialData: any = {}) => {
    setModalType(type);
    setModalMode(mode);
    setEditingId(initialData.id || null);

    // Setup form data depending on type
    if (type === "person") {
      const infoCopy = { ...(initialData.additional_info || {}) };
      delete infoCopy.age;
      const addInfoStr = mode === "edit" ? JSON.stringify(infoCopy, null, 2) : "{}";

      setFormData({
        name: initialData.name || "",
        age: initialData.additional_info?.age || "",
        notes: initialData.notes ? initialData.notes.join('\n') : "",
        additional_info: addInfoStr === "{}" ? "" : addInfoStr
      });
    } else if (type === "project") {
      const addInfoStr = mode === "edit" ? JSON.stringify(initialData.additional_info || {}, null, 2) : "{}";
      setFormData({
        title: initialData.title || "",
        status: initialData.status || "idea",
        description: initialData.description || "",
        additional_info: addInfoStr === "{}" ? "" : addInfoStr
      });
    } else if (type === "decision") {
      const addInfoStr = mode === "edit" ? JSON.stringify(initialData.additional_info || {}, null, 2) : "{}";
      setFormData({
        decision_name: initialData.decision_name || "",
        decision_text: initialData.decision_text || "",
        additional_info: addInfoStr === "{}" ? "" : addInfoStr
      });
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = await getToken();
      const headers = { Authorization: `Bearer ${token}` };

      let endpoint = `${BACKEND_URL}/${modalType === "person" ? "people" : modalType + "s"}`;
      let payload: any = {};

      if (modalType === "person") {
        let parsedInfo = {};
        if (formData.additional_info) {
          parsedInfo = JSON.parse(formData.additional_info);
        }
        payload = {
          name: formData.name,
          notes: formData.notes.split('\n').filter((n: string) => n.trim() !== ""),
          additional_info: { ...parsedInfo, age: formData.age }
        };
      } else if (modalType === "project") {
        let parsedInfo = {};
        if (formData.additional_info) {
          parsedInfo = JSON.parse(formData.additional_info);
        }
        payload = {
          title: formData.title,
          status: formData.status,
          description: formData.description,
          additional_info: parsedInfo
        };
      } else if (modalType === "decision") {
        let parsedInfo = {};
        if (formData.additional_info) {
          parsedInfo = JSON.parse(formData.additional_info);
        }
        payload = {
          decision_name: formData.decision_name || "Decision",
          decision_text: formData.decision_text,
          additional_info: parsedInfo
        };
      }

      if (modalMode === "add") {
        await axios.post(`${endpoint}/`, payload, { headers });
      } else {
        await axios.put(`${endpoint}/${editingId}`, payload, { headers });
      }

      closeModal();
      fetchData(); // Refresh all
    } catch (err) {
      console.error("Error saving entity", err);
      alert("Failed to save. Make sure your JSON (if any) is valid.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!editingId || !modalType) return;
    if (!confirm(`Are you sure you want to delete this ${modalType}?`)) return;

    setSaving(true);
    try {
      const token = await getToken();
      const headers = { Authorization: `Bearer ${token}` };
      const endpoint = `${BACKEND_URL}/${modalType === "person" ? "people" : modalType + "s"}`;

      await axios.delete(`${endpoint}/${editingId}`, { headers });
      closeModal();
      fetchData();
    } catch (err) {
      console.error("Error deleting entity", err);
      alert("Failed to delete.");
    } finally {
      setSaving(false);
    }
  };

  const closeModal = () => {
    setModalType(null);
    setFormData({});
  };

  const renderAdditionalInfo = (info: any) => {
    if (!info || Object.keys(info).length === 0) return null;
    return (
      <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(0,0,0,0.2)', borderRadius: '4px', fontSize: '0.8rem' }}>
        <strong style={{ opacity: 0.8, display: 'block', marginBottom: '4px' }}>Additional Info:</strong>
        <ul style={{ margin: 0, paddingLeft: '1.2rem', opacity: 0.9 }}>
          {Object.entries(info).map(([key, val]) => (
            <li key={key}><strong>{key}:</strong> {String(val)}</li>
          ))}
        </ul>
      </div>
    );
  };

  const headerStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'center' };
  const addBtnStyle = { background: 'var(--text-color)', color: 'var(--bg-color)', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 'bold' };
  const cardStyle = { background: 'var(--header-bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', position: 'relative' as any };

  if (loading && people.length === 0) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <PuffLoader color="#FFFBDE" size={100} />
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', height: '100%', overflowY: 'auto' }}>
      <h1>Knowledge Dashboard</h1>
      <p style={{ opacity: 0.7, marginBottom: '2rem' }}>Your Second Brain's structured entities.</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>

        {/* People Section */}
        <section>
          <div style={headerStyle}>
            <h2>👥 People</h2>
            <button style={addBtnStyle} onClick={() => openModal("person", "add")}>+ Add</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            {people.length === 0 ? <p>No people found.</p> : people.map((p, i) => {
              const info = p.additional_info || {};
              const age = info.age || "N/A";

              // Only render generic bullet points for keys OTHER than age
              const filteredInfo = { ...info };
              delete filteredInfo.age;

              return (
                <div key={i} style={cardStyle}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ fontSize: '1.2rem' }}>{p.name}</strong>
                    <button style={{ background: 'transparent', border: 'none', color: 'var(--text-color)', cursor: 'pointer', opacity: 0.6 }} onClick={() => openModal("person", "edit", p)}>✏️</button>
                  </div>

                  <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', opacity: 0.8, fontSize: '0.85rem' }}>
                    <span>🎂 {age} yrs</span>
                  </div>

                  <div style={{ margin: '0.8rem 0 0 0', opacity: 0.9, fontSize: '0.9rem' }}>
                    {p.notes && p.notes.length > 0 ? (
                      <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
                        {p.notes.map((note: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '4px' }}>{note}</li>
                        ))}
                      </ul>
                    ) : (
                      <p style={{ margin: 0, fontStyle: 'italic', opacity: 0.7 }}>No notes available.</p>
                    )}
                  </div>
                  {renderAdditionalInfo(filteredInfo)}
                  <small style={{ display: 'block', marginTop: '0.8rem', opacity: 0.5 }}>Last: {new Date(p.last_mentioned).toLocaleDateString()}</small>
                </div>
              );
            })}
          </div>
        </section>

        {/* Projects Section */}
        <section>
          <div style={headerStyle}>
            <h2>🚀 Projects</h2>
            <button style={addBtnStyle} onClick={() => openModal("project", "add")}>+ Add</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            {projects.length === 0 ? <p>No projects found.</p> : projects.map((p, i) => (
              <div key={i} style={cardStyle}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong>{p.title}</strong>
                  <button style={{ background: 'transparent', border: 'none', color: 'var(--text-color)', cursor: 'pointer', opacity: 0.6 }} onClick={() => openModal("project", "edit", p)}>✏️</button>
                </div>
                <span style={{ display: 'inline-block', marginTop: '5px', fontSize: '0.75rem', background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: '4px' }}>{p.status}</span>
                <p style={{ margin: '0.5rem 0 0 0', opacity: 0.8, fontSize: '0.9rem' }}>{p.description}</p>
                {renderAdditionalInfo(p.additional_info)}
                <small style={{ display: 'block', marginTop: '0.5rem', opacity: 0.5 }}>Last: {new Date(p.last_updated).toLocaleDateString()}</small>
              </div>
            ))}
          </div>
        </section>

        {/* Decisions Section */}
        <section>
          <div style={headerStyle}>
            <h2>🎯 Decisions</h2>
            <button style={addBtnStyle} onClick={() => openModal("decision", "add")}>+ Add</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            {decisions.length === 0 ? <p>No decisions found.</p> : decisions.map((d, i) => (
              <div key={i} style={cardStyle}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong>{d.decision_name || "Decision"}</strong>
                  <button style={{ background: 'transparent', border: 'none', color: 'var(--text-color)', cursor: 'pointer', opacity: 0.6 }} onClick={() => openModal("decision", "edit", d)}>✏️</button>
                </div>
                <p style={{ margin: '0.5rem 0 0 0', opacity: 0.8, fontSize: '0.9rem' }}>{d.decision_text}</p>
                {renderAdditionalInfo(d.additional_info)}
                <small style={{ display: 'block', marginTop: '0.5rem', opacity: 0.5 }}>Date: {new Date(d.date).toLocaleDateString()}</small>
              </div>
            ))}
          </div>
        </section>

      </div>

      {/* Generic Modal */}
      {modalType && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'var(--modal-bg, #2a2a2a)', padding: '2rem', borderRadius: '12px', width: '450px', maxWidth: '90%', maxHeight: '90vh', overflowY: 'auto' }}>
            <h3 style={{ marginTop: 0 }}>{modalMode === "add" ? "Add New" : "Edit"} {modalType === "person" ? "Person" : modalType === "project" ? "Project" : "Decision"}</h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>

              {modalType === "person" && (
                <>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Name *</label>
                    <input style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)' }} value={formData.name || ''} onChange={e => setFormData({ ...formData, name: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Age</label>
                    <input type="number" style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)' }} value={formData.age || ''} onChange={e => setFormData({ ...formData, age: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Notes (One per line)</label>
                    <textarea style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)', minHeight: '80px', resize: 'vertical' }} value={formData.notes || ''} onChange={e => setFormData({ ...formData, notes: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Additional Info (JSON)</label>
                    <textarea style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)', minHeight: '60px', resize: 'vertical', fontFamily: 'monospace' }} value={formData.additional_info || ''} onChange={e => setFormData({ ...formData, additional_info: e.target.value })} placeholder='{"hobby": "painting", "role": "manager"}' />
                  </div>
                </>
              )}

              {modalType === "project" && (
                <>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Title *</label>
                    <input style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)' }} value={formData.title || ''} onChange={e => setFormData({ ...formData, title: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Status</label>
                    <input style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)' }} value={formData.status || ''} onChange={e => setFormData({ ...formData, status: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Description</label>
                    <textarea style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)', minHeight: '80px', resize: 'vertical' }} value={formData.description || ''} onChange={e => setFormData({ ...formData, description: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Additional Info (JSON)</label>
                    <textarea style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)', minHeight: '60px', resize: 'vertical', fontFamily: 'monospace' }} value={formData.additional_info || ''} onChange={e => setFormData({ ...formData, additional_info: e.target.value })} placeholder='{"deadline": "2026", "priority": "high"}' />
                  </div>
                </>
              )}

              {modalType === "decision" && (
                <>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Decision Title</label>
                    <input style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)' }} value={formData.decision_name || ''} onChange={e => setFormData({ ...formData, decision_name: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Decision Text *</label>
                    <textarea style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)', minHeight: '80px', resize: 'vertical' }} value={formData.decision_text || ''} onChange={e => setFormData({ ...formData, decision_text: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Additional Info (JSON)</label>
                    <textarea style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)', minHeight: '60px', resize: 'vertical', fontFamily: 'monospace' }} value={formData.additional_info || ''} onChange={e => setFormData({ ...formData, additional_info: e.target.value })} placeholder='{"alternatives": "Option B", "confidence": "high"}' />
                  </div>
                </>
              )}

            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem' }}>
              <div>
                {modalMode === "edit" && (
                  <button style={{ padding: '6px 12px', background: 'rgba(255, 59, 48, 0.2)', border: '1px solid rgba(255, 59, 48, 0.5)', color: '#ff3b30', borderRadius: '6px', cursor: 'pointer' }} onClick={handleDelete} disabled={saving}>
                    Delete
                  </button>
                )}
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button style={{ padding: '6px 12px', background: 'transparent', border: '1px solid var(--border-color)', color: 'white', borderRadius: '6px', cursor: 'pointer' }} onClick={closeModal}>Cancel</button>
                <button style={{ padding: '6px 16px', background: '#FFFBDE', border: 'none', color: '#1a1a1a', fontWeight: 'bold', borderRadius: '6px', cursor: 'pointer' }} onClick={handleSave} disabled={saving}>
                  {saving ? "Saving..." : "Save"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
