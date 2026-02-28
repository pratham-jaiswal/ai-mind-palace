import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@clerk/clerk-react';
import { PuffLoader } from 'react-spinners';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function Dashboard() {
  const { getToken } = useAuth();
  const [people, setPeople] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [decisions, setDecisions] = useState<any[]>([]);
  const [memories, setMemories] = useState<any[]>([]);
  const [selfPerson, setSelfPerson] = useState<any>(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState("");

  const [loadingPeople, setLoadingPeople] = useState(true);
  const [loadingSelf, setLoadingSelf] = useState(true);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [loadingDecisions, setLoadingDecisions] = useState(true);
  const [loadingMemories, setLoadingMemories] = useState(true);

  // Pagination State
  const [peoplePage, setPeoplePage] = useState(1);
  const [projectsPage, setProjectsPage] = useState(1);
  const [decisionsPage, setDecisionsPage] = useState(1);
  const [memoriesPage, setMemoriesPage] = useState(1);

  const [peopleTotal, setPeopleTotal] = useState(0);
  const [projectsTotal, setProjectsTotal] = useState(0);
  const [decisionsTotal, setDecisionsTotal] = useState(0);
  const [memoriesTotal, setMemoriesTotal] = useState(0);

  const defaultLimit = parseInt(import.meta.env.VITE_PAGINATION_LIMIT || '10', 10);
  const limit = isNaN(defaultLimit) ? 10 : defaultLimit;

  // Modal State
  const [modalType, setModalType] = useState<"person" | "project" | "decision" | "memory" | null>(null);
  const [modalMode, setModalMode] = useState<"add" | "edit">("add");
  const [editingId, setEditingId] = useState<number | string | null>(null);

  // Form State
  const [formData, setFormData] = useState<any>({});
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchSelf();
    fetchPeople();
    fetchProjects();
    fetchDecisions();
    fetchMemories();
  }, [getToken]); // Only run on mount or token change

  // When pagination or search query changes, fetch specific data
  useEffect(() => { fetchPeople(); }, [peoplePage, debouncedSearchQuery]);
  useEffect(() => { fetchProjects(); }, [projectsPage, debouncedSearchQuery]);
  useEffect(() => { fetchDecisions(); }, [decisionsPage, debouncedSearchQuery]);
  useEffect(() => { fetchMemories(); }, [memoriesPage, debouncedSearchQuery]);

  // Reset pagination to page 1 whenever search query changes
  useEffect(() => {
    setPeoplePage(1);
    setProjectsPage(1);
    setDecisionsPage(1);
    setMemoriesPage(1);
  }, [debouncedSearchQuery]);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 500);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  const fetchSelf = async () => {
    setLoadingSelf(true);
    try {
      const token = await getToken();
      const res = await axios.get(`${BACKEND_URL}/people/self`, { headers: { Authorization: `Bearer ${token}` } });
      setSelfPerson(res.data.result);
    } catch (err) {
      console.error(err);
      setSelfPerson(null);
    } finally {
      setLoadingSelf(false);
    }
  };

  const fetchPeople = async () => {
    setLoadingPeople(true);
    try {
      const token = await getToken();
      const res = await axios.get(`${BACKEND_URL}/people/?page=${peoplePage}&limit=${limit}&q=${encodeURIComponent(debouncedSearchQuery)}`, { headers: { Authorization: `Bearer ${token}` } });
      const payload = res.data.result || {};
      const fetchedPeople = payload.result || [];
      // Note: "self" and "me" are now excluded gracefully by the backend SQL filter.
      setPeople(fetchedPeople);
      setPeopleTotal(payload.total || 0);
    } catch (err) { console.error(err); } finally { setLoadingPeople(false); }
  };

  const fetchProjects = async () => {
    setLoadingProjects(true);
    try {
      const token = await getToken();
      const res = await axios.get(`${BACKEND_URL}/projects/?page=${projectsPage}&limit=${limit}&q=${encodeURIComponent(debouncedSearchQuery)}`, { headers: { Authorization: `Bearer ${token}` } });
      const payload = res.data.result || {};
      setProjects(payload.result || []);
      setProjectsTotal(payload.total || 0);
    } catch (err) { console.error(err); } finally { setLoadingProjects(false); }
  };

  const fetchDecisions = async () => {
    setLoadingDecisions(true);
    try {
      const token = await getToken();
      const res = await axios.get(`${BACKEND_URL}/decisions/?page=${decisionsPage}&limit=${limit}&q=${encodeURIComponent(debouncedSearchQuery)}`, { headers: { Authorization: `Bearer ${token}` } });
      const payload = res.data.result || {};
      const fetchedDecisions = payload.result || [];
      fetchedDecisions.sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime());
      setDecisions(fetchedDecisions);
      setDecisionsTotal(payload.total || 0);
    } catch (err) { console.error(err); } finally { setLoadingDecisions(false); }
  };

  const fetchMemories = async () => {
    setLoadingMemories(true);
    try {
      const token = await getToken();
      const res = await axios.get(`${BACKEND_URL}/memories/?page=${memoriesPage}&limit=${limit}&q=${encodeURIComponent(debouncedSearchQuery)}`, { headers: { Authorization: `Bearer ${token}` } });
      const payload = res.data.result || {};
      setMemories(payload.result || []);
      setMemoriesTotal(payload.total || 0);
    } catch (err) { console.error(err); } finally { setLoadingMemories(false); }
  };

  // const fetchData = () => {
  //   fetchSelf();
  //   fetchPeople();
  //   fetchProjects();
  //   fetchDecisions();
  //   fetchMemories();
  // };

  const openModal = (type: "person" | "project" | "decision" | "memory", mode: "add" | "edit", initialData: any = {}) => {
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
    } else if (type === "memory") {
      setFormData({
        content: initialData.content || ""
      });
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = await getToken();
      const headers = { Authorization: `Bearer ${token}` };

      let endpoint = modalType === "memory" ? `${BACKEND_URL}/memories` : `${BACKEND_URL}/${modalType === "person" ? "people" : modalType + "s"}`;
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
        if (formData.additional_info) parsedInfo = JSON.parse(formData.additional_info);
        payload = {
          decision_name: formData.decision_name || "Decision",
          decision_text: formData.decision_text,
          additional_info: parsedInfo
        };
      } else if (modalType === "memory") {
        payload = {
          content: formData.content
        };
      }

      if (modalMode === "add") {
        await axios.post(`${endpoint}/`, payload, { headers });
      } else {
        await axios.put(`${endpoint}/${editingId}`, payload, { headers });
      }

      closeModal();
      if (modalType === "person") {
        const n = (formData.name || "").toLowerCase();
        if (n === "self" || n === "me") fetchSelf();
        else fetchPeople();
      }
      else if (modalType === "project") fetchProjects();
      else if (modalType === "decision") fetchDecisions();
      else if (modalType === "memory") fetchMemories();
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

    setDeleting(true);
    try {
      const token = await getToken();
      const headers = { Authorization: `Bearer ${token}` };
      const endpoint = modalType === "memory" ? `${BACKEND_URL}/memories` : `${BACKEND_URL}/${modalType === "person" ? "people" : modalType + "s"}`;

      await axios.delete(`${endpoint}/${editingId}`, { headers });
      closeModal();
      if (modalType === "person") {
        if (selfPerson && editingId === selfPerson.id) fetchSelf();
        else fetchPeople();
      }
      else if (modalType === "project") fetchProjects();
      else if (modalType === "decision") fetchDecisions();
      else if (modalType === "memory") fetchMemories();
    } catch (err) {
      console.error("Error deleting entity", err);
      alert("Failed to delete.");
    } finally {
      setDeleting(false);
    }
  };

  const closeModal = () => {
    setModalType(null);
    setFormData({});
  };

  const renderAdditionalInfo = (info: any) => {
    if (!info || Object.keys(info).length === 0) return null;
    return (
      <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(0,0,0,0.2)', borderRadius: '4px', fontSize: '0.8rem', width: '100%', boxSizing: 'border-box' }}>
        <strong style={{ opacity: 0.8, display: 'block', marginBottom: '4px' }}>Additional Info:</strong>
        <ul style={{ margin: 0, paddingLeft: '1.2rem', opacity: 0.9, wordBreak: 'break-all', overflowWrap: 'anywhere' }}>
          {Object.entries(info).map(([key, val]) => (
            <li key={key}><strong>{key}:</strong> {String(val)}</li>
          ))}
        </ul>
      </div>
    );
  };

  const headerStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'center' };
  const addBtnStyle = { background: 'var(--text-color)', color: 'var(--bg-color)', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 'bold' };
  const cardStyle = { background: 'var(--header-bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', position: 'relative' as any, wordBreak: 'break-word' as any, overflowWrap: 'anywhere' as any };

  const renderPagination = (currentPage: number, totalItems: number, setPage: (p: number) => void) => {
    const totalPages = Math.ceil(totalItems / limit);
    if (totalPages <= 1) return null;
    return (
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
        <button
          style={{ ...addBtnStyle, opacity: currentPage === 1 ? 0.5 : 1 }}
          disabled={currentPage === 1}
          onClick={() => setPage(currentPage - 1)}
        >
          &lt; Previous
        </button>
        <span style={{ fontSize: '0.9rem', opacity: 0.8 }}>Page {currentPage} of {totalPages}</span>
        <button
          style={{ ...addBtnStyle, opacity: currentPage === totalPages ? 0.5 : 1 }}
          disabled={currentPage === totalPages}
          onClick={() => setPage(currentPage + 1)}
        >
          Next &gt;
        </button>
      </div>
    );
  };

  if (loadingPeople && people.length === 0 && loadingProjects && projects.length === 0) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <PuffLoader color="#FFFBDE" size={100} />
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', height: '100%', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1 }}>
        {/* <h1>Knowledge Dashboard</h1> */}
        {/* <p style={{ opacity: 0.7, marginBottom: '2rem' }}>Your Second Brain's structured entities.</p> */}

        <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'center' }}>
          <div style={{ position: 'relative', width: '100%', maxWidth: '600px' }}>
            <span style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', opacity: 0.5 }}>🔍</span>
            <input
              type="text"
              placeholder="Search Knowledge Base..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: '100%', padding: '12px 20px 12px 45px', fontSize: '1rem', borderRadius: '24px', border: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.1)', color: 'var(--text-color)', outline: 'none', transition: 'box-shadow 0.2s', boxSizing: 'border-box' }}
              onFocus={(e) => e.target.style.boxShadow = '0 0 0 2px var(--border-color)'}
              onBlur={(e) => e.target.style.boxShadow = 'none'}
            />
          </div>
        </div>

        {/* Your Profile Section */}
        <section style={{ marginBottom: '2rem' }}>
          <div style={{ ...headerStyle, borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
            <h2>🧑 Your Profile {loadingSelf && <PuffLoader color="#FFFBDE" size={20} cssOverride={{ display: 'inline-block', marginLeft: '10px' }} />}</h2>
            {!selfPerson && <button style={addBtnStyle} onClick={() => openModal("person", "add", { name: "me" })}>+ Add Profile</button>}
          </div>
          <div style={{ marginTop: '1rem' }}>
            {!selfPerson && !loadingSelf ? (
              <p style={{ opacity: 0.6 }}>You haven't set up your profile yet.</p>
            ) : selfPerson ? (
              <div style={{ ...cardStyle, maxWidth: '600px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1, minWidth: 0, paddingRight: '1rem' }}>
                  <h3 style={{ margin: '0 0 0.5rem 0' }}>{selfPerson.name} {selfPerson.additional_info?.age ? `(${selfPerson.additional_info.age})` : ''}</h3>
                  {(selfPerson.notes && selfPerson.notes.length > 0) && (
                    <ul style={{ margin: 0, paddingLeft: '1.2rem', opacity: 0.8, fontSize: '0.9rem', paddingBottom: '0.5rem' }}>
                      {selfPerson.notes.map((n: string, idx: number) => <li key={idx}>{n}</li>)}
                    </ul>
                  )}
                  {renderAdditionalInfo(
                    Object.fromEntries(
                      Object.entries(selfPerson.additional_info || {}).filter(([k]) => k !== 'age')
                    )
                  )}
                </div>
                <button style={{ background: 'transparent', border: 'none', color: 'var(--text-color)', cursor: 'pointer', opacity: 0.6 }} onClick={() => openModal("person", "edit", selfPerson)}>✏️</button>
              </div>
            ) : null}
          </div>
        </section>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>

          {/* Memories Section */}
          <section>
            <div style={headerStyle}>
              <h2>🧠 Memories {loadingMemories && <PuffLoader color="#FFFBDE" size={20} cssOverride={{ display: 'inline-block', marginLeft: '10px' }} />}</h2>
              <button style={addBtnStyle} onClick={() => openModal("memory", "add")}>+ Add</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
              {memories.length === 0 ? <p>No memories found.</p> : memories.map((m, i) => (
                <div key={i} style={cardStyle}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <p style={{ margin: '0 0 0.5rem 0', opacity: 0.9, fontSize: '0.9rem', whiteSpace: 'pre-wrap', flex: 1 }}>
                      {m.content}
                    </p>
                    <button style={{ background: 'transparent', border: 'none', color: 'var(--text-color)', cursor: 'pointer', opacity: 0.6, marginLeft: '10px' }} onClick={() => openModal("memory", "edit", { id: m.metadata.id, content: m.content })}>✏️</button>
                  </div>
                </div>
              ))}
            </div>
            {renderPagination(memoriesPage, memoriesTotal, setMemoriesPage)}
          </section>

          {/* People Section */}
          <section>
            <div style={headerStyle}>
              <h2>👥 People {loadingPeople && <PuffLoader color="#FFFBDE" size={20} cssOverride={{ display: 'inline-block', marginLeft: '10px' }} />}</h2>
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
            {renderPagination(peoplePage, peopleTotal, setPeoplePage)}
          </section>

          {/* Projects Section */}
          <section>
            <div style={headerStyle}>
              <h2>🚀 Projects {loadingProjects && <PuffLoader color="#FFFBDE" size={20} cssOverride={{ display: 'inline-block', marginLeft: '10px' }} />}</h2>
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
            {renderPagination(projectsPage, projectsTotal, setProjectsPage)}
          </section>

          {/* Decisions Section */}
          <section>
            <div style={headerStyle}>
              <h2>🎯 Decisions {loadingDecisions && <PuffLoader color="#FFFBDE" size={20} cssOverride={{ display: 'inline-block', marginLeft: '10px' }} />}</h2>
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
            {renderPagination(decisionsPage, decisionsTotal, setDecisionsPage)}
          </section>

        </div>

        {/* Generic Modal */}
        {modalType && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
            <div style={{ background: 'var(--modal-bg, #2a2a2a)', padding: '2rem', borderRadius: '12px', width: '450px', maxWidth: '90%', maxHeight: '90vh', overflowY: 'auto' }}>
              <h3 style={{ marginTop: 0 }}>{modalMode === "add" ? "Add New" : "Edit"} {modalType === "person" ? "Person" : modalType === "project" ? "Project" : modalType === "memory" ? "Memory" : "Decision"}</h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>

                {modalType === "memory" && (
                  <div>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', opacity: 0.8 }}>Memory Content *</label>
                    <textarea style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--header-bg)', color: 'var(--text-color)', minHeight: '120px', resize: 'vertical' }} value={formData.content || ''} onChange={e => setFormData({ ...formData, content: e.target.value })} />
                  </div>
                )}

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
                    <button style={{ padding: '6px 12px', background: 'rgba(255, 59, 48, 0.2)', border: '1px solid rgba(255, 59, 48, 0.5)', color: '#ff3b30', borderRadius: '6px', cursor: 'pointer' }} onClick={handleDelete} disabled={saving || deleting}>
                      {deleting ? "Deleting..." : "Delete"}
                    </button>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button style={{ padding: '6px 12px', background: 'transparent', border: '1px solid var(--border-color)', color: 'white', borderRadius: '6px', cursor: 'pointer' }} onClick={closeModal} disabled={saving || deleting}>Cancel</button>
                  <button style={{ padding: '6px 16px', background: '#FFFBDE', border: 'none', color: '#1a1a1a', fontWeight: 'bold', borderRadius: '6px', cursor: 'pointer' }} onClick={handleSave} disabled={saving || deleting}>
                    {saving ? "Saving..." : "Save"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Global Dashboard Footer */}
      <footer style={{ marginTop: '3rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)', textAlign: 'center', fontSize: '0.85rem', color: 'var(--subtext-color)', paddingBottom: '1rem' }}>
        <span>AI can make mistakes. Consider verifying important information.</span>
        <span style={{ margin: '0 8px', opacity: 0.4 }}>|</span>
        <span>&copy; {new Date().getFullYear()} Pratham Jaiswal</span>
        <span style={{ margin: '0 8px', opacity: 0.4 }}>|</span>
        <a href="https://github.com/pratham-jaiswal/ai-mind-palace" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--subtext-color)', textDecoration: 'none', opacity: 0.8 }}>GitHub</a>
        <span style={{ margin: '0 8px', opacity: 0.4 }}>|</span>
        <Link to="/terms" style={{ color: 'var(--subtext-color)', textDecoration: 'none', opacity: 0.8 }}>Terms</Link>
        <span style={{ margin: '0 8px', opacity: 0.4 }}>|</span>
        <Link to="/privacy" style={{ color: 'var(--subtext-color)', textDecoration: 'none', opacity: 0.8 }}>Privacy</Link>
      </footer>

    </div>
  );
}
