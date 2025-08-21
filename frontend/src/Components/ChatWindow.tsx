import { useEffect, useRef, useState } from "react";
import axios from "axios";
import "./ChatWindow.css";
import ReactMarkdown from "react-markdown";
import { useAuth } from "@clerk/clerk-react";
import { ToastContainer, toast, Bounce } from "react-toastify";
import { PuffLoader } from "react-spinners";

type Message = {
  role: string;
  content: string;
  isPlaceholder?: boolean;
};

type ConversationMetadata = {
  date: string;
  thread_id: string;
  title: string;
};

const ChatWindow = () => {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const [conversations, setConversations] = useState<ConversationMetadata[]>(
    []
  );
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [conversationToDelete, setConversationToDelete] =
    useState<ConversationMetadata | null>(null);

  const [loadingConversations, setLoadingConversations] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);

  const fetchConversations = async () => {
    try {
      const token = await getToken();
      const res = await axios.get(
        `${import.meta.env.VITE_BACKEND_URL}/conversation/fetch`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          withCredentials: true,
        }
      );
      setConversations(res.data.result || []);
    } catch (err: any) {
      toast.error("Failed to fetch conversations", {
        position: "top-right",
        autoClose: 3000,
        theme: "dark",
        transition: Bounce,
      });
    } finally {
      setLoadingConversations(false);
    }
  };

  useEffect(() => {
    setLoadingConversations(true);
    fetchConversations();
  }, [getToken]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const fetchConversationData = async (selectedThreadId: string) => {
    try {
      setMessages([]);
      setLoadingMessages(true);
      setThreadId(selectedThreadId);
      const token = await getToken();
      const res = await axios.get(
        `${
          import.meta.env.VITE_BACKEND_URL
        }/conversation/fetch/${selectedThreadId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          withCredentials: true,
        }
      );
      setMessages(res.data.result || []);
    } catch (err: any) {
      setThreadId(null);
      toast.error("Failed to fetch conversations", {
        position: "top-right",
        autoClose: 3000,
        theme: "dark",
        transition: Bounce,
      });
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    const placeholderAIMessage = {
      role: "ai",
      content: "*Generating...*",
      isPlaceholder: true,
    };
    const updatedMessages = [...messages, userMessage, placeholderAIMessage];
    setMessages(updatedMessages);

    const token = await getToken();
    axios
      .post(
        `${import.meta.env.VITE_BACKEND_URL}/invoke/`,
        {
          user_query: input,
          provider: "gemini",
          model: "gemini-2.0-flash",
          temperature: 0.3,
          thread_id: threadId,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          withCredentials: true,
        }
      )
      .then((res) => {
        const result = res.data.result;

        if (result.thread_id && threadId !== result.thread_id) {
          return fetchConversations().then(() => {
            setThreadId(result.thread_id);
            return result;
          });
        }
        return result;
      })
      .then((result) => {
        const aiMessage = {
          role: "ai",
          content: result.response,
        };

        setMessages((prev) => [...prev.slice(0, -1), aiMessage]);
      })
      .catch((err) => {
        if (err.response && err.response.status === 401) {
          toast.error("Unauthorized access. Please log in again.", {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: false,
            closeOnClick: false,
            pauseOnHover: false,
            draggable: true,
            progress: undefined,
            theme: "dark",
            transition: Bounce,
          });
        } else {
          toast.error("An error occurred while processing your request.", {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: false,
            closeOnClick: false,
            pauseOnHover: false,
            draggable: true,
            progress: undefined,
            theme: "dark",
            transition: Bounce,
          });
        }
        const updatedMessages = messages.slice(0, -1);
        setMessages(updatedMessages);
      });

    setInput("");
  };

  const handleNewConversation = async () => {
    setThreadId(null);
    setMessages([]);
  };

  const handleDeleteConversation = async (selectedThreadId: string) => {
    try {
      const token = await getToken();
      const res = await axios.delete(
        `${import.meta.env.VITE_BACKEND_URL}/conversation/delete`,
        {
          data: { conversation_id: selectedThreadId },
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          withCredentials: true,
        }
      );
      if (!res.data?.result?.deleted) {
        throw new Error("Failed to delete conversation");
      }
      toast.success("Conversation deleted successfully", {
        position: "top-right",
        autoClose: 3000,
        theme: "dark",
        transition: Bounce,
      });
      if (selectedThreadId === threadId) {
        setThreadId(null);
        setMessages([]);
      }
      const updatedConversations = conversations.filter(
        (c) => c.thread_id !== selectedThreadId
      );
      setConversations(updatedConversations);
    } catch (err: any) {
      setThreadId(null);
      toast.error("Failed to delete conversations", {
        position: "top-right",
        autoClose: 3000,
        theme: "dark",
        transition: Bounce,
      });
    } finally {
      setShowDeleteModal(false);
      setConversationToDelete(null);
    }
  };

  if (loadingConversations) {
    return (
      <div className="loader">
        <PuffLoader
          color="rgb(250, 240, 230)"
          size={100}
          loading={loadingConversations}
        />
      </div>
    );
  }

  return (
    <div className="chat-layout">
      <div className={`sidebar ${sidebarOpen ? "open" : "collapsed"}`}>
        <div className="sidebar-header">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="sidebar-header-btn"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              height="20px"
              viewBox="120 -840 720 720"
              width="20px"
            >
              <path
                d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm120-80v-560H200v560h120Zm80 0h360v-560H400v560Zm-80 0H200h120Z"
                fill="#FFFBDE"
              />
            </svg>
          </button>
          <button
            onClick={handleNewConversation}
            className="sidebar-header-btn"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              height="20px"
              viewBox="120 -921 800 801"
              width="20px"
            >
              <path
                d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h357l-80 80H200v560h560v-278l80-80v358q0 33-23.5 56.5T760-120H200Zm280-360ZM360-360v-170l367-367q12-12 27-18t30-6q16 0 30.5 6t26.5 18l56 57q11 12 17 26.5t6 29.5q0 15-5.5 29.5T897-728L530-360H360Zm481-424-56-56 56 56ZM440-440h56l232-232-28-28-29-28-231 231v57Zm260-260-29-28 29 28 28 28-28-28Z"
                fill="#FFFBDE"
              />
            </svg>
          </button>
        </div>
        {sidebarOpen && (
          <>
            <div className="conversation-list-header">Chats</div>
            <ul className="conversation-list">
              {conversations.map((c, idx) => (
                <li
                  key={idx}
                  className={
                    "conversation-item " +
                    (c.thread_id === threadId ? "active" : "")
                  }
                  onClick={() => fetchConversationData(c.thread_id)}
                >
                  <div className="conversation-title">{c.title}</div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setConversationToDelete({
                        date: c.date,
                        thread_id: c.thread_id,
                        title: c.title,
                      });
                      setShowDeleteModal(true);
                    }}
                    className="conversation-delete-btn"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      height="18px"
                      viewBox="120 -921 800 801"
                      width="18px"
                    >
                      <path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z" />
                    </svg>
                  </button>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>

      <div className="chat-window">
        {messages.length === 0 && !loadingMessages ? (
          <div className="empty-state">
            <p className="prompt-text">What's your query?</p>
            <div className="input-container centered">
              <input
                className="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Type a message..."
              />
              <button className="send-button" onClick={handleSend}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  height="24px"
                  viewBox="0 -960 960 960"
                  width="24px"
                  fill="#FFFBDE"
                >
                  <path d="M120-160v-640l760 320-760 320Zm80-120 474-200-474-200v140l240 60-240 60v140Zm0 0v-400 400Z" />
                </svg>
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  {msg.role === "ai" ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    <>{msg.content}</>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />{" "}
            </div>
            <div className="input-container">
              <input
                className="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Type a message..."
              />
              <button className="send-button" onClick={handleSend}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  height="24px"
                  viewBox="0 -960 960 960"
                  width="24px"
                  fill="#FFFBDE"
                >
                  <path d="M120-160v-640l760 320-760 320Zm80-120 474-200-474-200v140l240 60-240 60v140Zm0 0v-400 400Z" />
                </svg>
              </button>
            </div>
            <p className="disclaimer">
              Powered by OpenAI. AI can make mistakes.
            </p>
          </>
        )}
        <ToastContainer />
      </div>

      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">Delete Chat?</div>
            <p>
              This will delete conversation{" "}
              <strong>{conversationToDelete?.title}</strong>, but any saved
              memories or tasks will be retained.
            </p>
            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => {
                  setShowDeleteModal(false);
                  setConversationToDelete(null);
                }}
              >
                Cancel
              </button>
              <button
                className="btn-delete"
                onClick={() => {
                  if (conversationToDelete) {
                    handleDeleteConversation(conversationToDelete?.thread_id);
                  }
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
