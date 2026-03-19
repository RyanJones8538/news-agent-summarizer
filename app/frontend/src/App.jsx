import { useEffect, useState } from "react";
import TopicForm from "./components/TopicForm";
import TopicList from "./components/TopicList";
import MessageDisplay from "./components/MessageDisplay";
import {
  getTopics,
  fetchTopic,
  analyzeTopic,
  deleteTopic,
  clearDatabase,
} from "./api";

export default function App() {
  const [topics, setTopics] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadTopics() {
    try {
      const data = await getTopics();
      setTopics(data.topics);
    } catch (err) { 
      setError(err.message);
    }
  }

  useEffect(() => {
    loadTopics();
  }, []);

  async function runAction(action) {
    setLoading(true);
    setError("");
    setMessage("");

      try { 
        const data = await action();
        setMessage(data.message || "");
        await loadTopics();
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
  }
  
  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>News Agent</h1>

      <TopicForm
        label="Topic"
        buttonText="Fetch"
        onSubmit={(topic) => runAction(() => fetchTopic(topic))}
      />

      <TopicForm
        label="Topic"
        buttonText="Analyze"
        onSubmit={(topic) => runAction(() => analyzeTopic(topic))}
      />

      <TopicForm
        label="Topic"
        buttonText="Delete Topic"
        onSubmit={(topic) => runAction(() => deleteTopic(topic))}
      />

      <button
        onClick={() => runAction(() => clearDatabase())}
        disabled={loading}
      >
        Clear Database
      </button>

      {loading && <p>Loading...</p>}

      <TopicList topics={topics} />
      <MessageDisplay message={message} error={error} />
    </div>
  );

}