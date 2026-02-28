import { useEffect, useState, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  addEdge,
} from 'reactflow';
import type { Connection, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';
import { useAuth } from '@clerk/clerk-react';
import { PuffLoader } from 'react-spinners';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function MindMap() {
  const { getToken } = useAuth();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);

  // Data State
  const [peopleData, setPeopleData] = useState<any[]>([]);
  const [projectsData, setProjectsData] = useState<any[]>([]);
  const [decisionsData, setDecisionsData] = useState<any[]>([]);

  // Modal State
  const [modalType, setModalType] = useState<"person" | "project" | "decision" | null>(null);
  const [modalMode, setModalMode] = useState<"add" | "edit">("edit");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<any>({});
  const [saving, setSaving] = useState(false);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const token = await getToken();
      const headers = { Authorization: `Bearer ${token}` };

      const [resPeople, resProjects, resDecisions] = await Promise.all([
        axios.get(`${BACKEND_URL}/people/`, { headers }),
        axios.get(`${BACKEND_URL}/projects/`, { headers }),
        axios.get(`${BACKEND_URL}/decisions/`, { headers })
      ]);

      const peoplePayload = resPeople.data.result || {};
      const projectsPayload = resProjects.data.result || {};
      const decisionsPayload = resDecisions.data.result || {};

      const people = peoplePayload.result || [];
      const projects = projectsPayload.result || [];
      const decisions = decisionsPayload.result || [];

      setPeopleData(people);
      setProjectsData(projects);
      setDecisionsData(decisions);

      const newNodes: any[] = [];
      const newEdges: any[] = [];

      // Add a central node for the User
      const centerId = 'user-center';
      const centerX = 400;
      const centerY = 300;

      newNodes.push({
        id: centerId,
        position: { x: centerX, y: centerY },
        data: { label: 'You' },
        style: { background: '#FFFBDE', color: '#1a1a1a', fontWeight: 'bold' }
      });

      // Helper function to distribute nodes in a semicircle/arc
      const addNodesInArc = (items: any[], type: string, radius: number, startAngle: number, endAngle: number) => {
        const total = items.length;
        if (total === 0) return;

        const angleStep = total === 1 ? 0 : (endAngle - startAngle) / (total - 1);

        items.forEach((item: any, i: number) => {
          const angle = startAngle + (angleStep * i);
          const x = centerX + radius * Math.cos(angle);
          const y = centerY + radius * Math.sin(angle);
          const id = `${type}-${item.id}`;

          if (type === 'person') {
            const info = item.additional_info || {};
            const age = info.age ? `${info.age}y` : "N/A";
            const relLabel = info.relationship || info.relation || "";

            const labelHtml = (
              <div style={{ padding: '5px', textAlign: 'center' }}>
                <div style={{ fontWeight: 'bold' }}>👤 {item.name} {relLabel ? `(${relLabel})` : ""}</div>
                <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '4px' }}>
                  🎂 {age}
                </div>
              </div>
            );

            newNodes.push({
              id, position: { x, y }, data: { label: labelHtml },
              style: { width: 160, padding: 0, background: '#E3F2FD', color: '#0D47A1', border: '1px solid #90CAF9', borderRadius: '8px' }
            });
            newEdges.push({ id: `e-${centerId}-${id}`, source: centerId, target: id, animated: true });

          } else if (type === 'project') {
            const projectStatusHtml = item.status ? (
              <div style={{ padding: '5px', textAlign: 'center' }}>
                <div style={{ fontWeight: 'bold' }}>🚀 {item.title}</div>
                <div style={{ fontSize: '0.75rem', opacity: 0.8, marginTop: '4px', background: 'rgba(0,0,0,0.1)', display: 'inline-block', padding: '2px 6px', borderRadius: '4px' }}>
                  {item.status}
                </div>
              </div>
            ) : `🚀 ${item.title}`;

            newNodes.push({
              id, position: { x, y }, data: { label: projectStatusHtml },
              style: { background: '#F3E5F5', color: '#4A148C', border: '1px solid #CE93D8', borderRadius: '8px', padding: '10px' }
            });
            newEdges.push({ id: `e-${centerId}-${id}`, source: centerId, target: id, animated: true });

          } else if (type === 'decision') {
            newNodes.push({
              id, position: { x, y }, data: { label: `🎯 ${item.decision_text.length > 20 ? item.decision_text.substring(0, 20) + '...' : item.decision_text}` },
              style: { background: '#E8F5E9', color: '#1B5E20', border: '1px solid #A5D6A7', borderRadius: '8px', padding: '10px' }
            });
            newEdges.push({ id: `e-${centerId}-${id}`, source: centerId, target: id, animated: true });
          }
        });
      };

      // Distribute People to the Left Arc (approx 135 to 225 degrees)
      const peopleRadius = 450 + (people.length * 20);
      addNodesInArc(people, 'person', peopleRadius, Math.PI * 0.75, Math.PI * 1.25);

      // Distribute Projects to the Right Arc (approx -45 to 45 degrees)
      const projectRadius = 450 + (projects.length * 20);
      addNodesInArc(projects, 'project', projectRadius, -Math.PI * 0.25, Math.PI * 0.25);

      // Distribute Decisions to the Bottom Arc (approx 63 to 117 degrees)
      const decisionRadius = 350 + (decisions.length * 20);
      addNodesInArc(decisions, 'decision', decisionRadius, Math.PI * 0.35, Math.PI * 0.65);

      setNodes(newNodes);
      setEdges(newEdges);
    } catch (err) {
      console.error("Error fetching mind map data", err);
    } finally {
      setLoading(false);
    }
  }, [getToken, setNodes, setEdges]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const openModal = (type: "person" | "project" | "decision", mode: "add" | "edit", initialData: any = {}) => {
    setModalType(type);
    setModalMode(mode);
    setEditingId(initialData.id || null);

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
        if (formData.additional_info) parsedInfo = JSON.parse(formData.additional_info);
        payload = {
          name: formData.name,
          notes: formData.notes ? formData.notes.split('\n').filter((n: string) => n.trim() !== "") : [],
          additional_info: { ...parsedInfo, age: formData.age }
        };
      } else if (modalType === "project") {
        let parsedInfo = {};
        if (formData.additional_info) parsedInfo = JSON.parse(formData.additional_info);
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
      }

      if (modalMode === "add") {
        await axios.post(`${endpoint}/`, payload, { headers });
      } else {
        await axios.put(`${endpoint}/${editingId}`, payload, { headers });
      }

      closeModal();
      fetchData();
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

  const onNodeClick = (event: React.MouseEvent, node: any) => {
    event.preventDefault();
    const parts = node.id.split('-');
    if (parts.length < 2) return;
    const type = parts[0];
    const id = parseInt(parts[1], 10);

    if (type === 'person') {
      const p = peopleData.find(x => x.id === id);
      if (p) openModal('person', 'edit', p);
    } else if (type === 'project') {
      const p = projectsData.find(x => x.id === id);
      if (p) openModal('project', 'edit', p);
    } else if (type === 'decision') {
      const d = decisionsData.find(x => x.id === id);
      if (d) openModal('decision', 'edit', d);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <PuffLoader color="#FFFBDE" size={100} />
      </div>
    );
  }

  return (
    <div style={{ width: '100vw', height: 'calc(100vh - 65px)' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        proOptions={{ hideAttribution: true }}
        fitView
      >
        <Controls />
        <MiniMap
          style={{ background: 'var(--header-bg, #1a1a1a)', border: '1px solid var(--border-color, #333)', borderRadius: '8px' }}
          maskColor="rgba(0, 0, 0, 0.5)"
          nodeColor="var(--text-color, #FFFBDE)"
        />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>

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
