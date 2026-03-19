import {useState} from "react";

export default function TopicForm({label, buttonText, onSubmit}) {
    const [topic, setTopic] = useState("");

    async function handleSubmit(e) {
        e.preventDefault();

        const trimmed = topic.trim();
        if(!trimmed) return;

        await onSubmit(trimmed);
        setTopic("");
    }

    return (
        <form onSubmit={handleSubmit} style={{ marginBottom: "1rem"}}>
            <input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder={label}
            />
            <button type="submit" style={{ marginLeft: "0.5rem"}}>
                {buttonText}
            </button>
        
        </form>
    );
}