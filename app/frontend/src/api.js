const API_BASE = "/api";

async function processResponse(response) {
    if (!contentType.includes("application/json")) {
        const text = await response.text();
        throw new Error(text || "Server returned a non-JSON response");
    }

    const data = await response.json();

    if(!response.ok) {
        throw new Error(data.detail || "Error Encountered.");
    }

    return data;
}

export async function getTopics() {
    const response = await fetch(`${API_BASE}/topics`);
    return processResponse(response);
}

export async function fetchTopic(topic) {
    const response = await fetch(`${API_BASE}/fetch`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({topic}),

    });

    return processResponse(response);
}

export async function analyzeTopic(topic) {
    const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({topic}),
    });

    return processResponse(response);
}

export async function deleteTopic(topic) {
    const response = await fetch(`${API_BASE}/delete_topic`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({topic}),

    });

    return processResponse(response);
}

export async function clearDatabase() {
    const response = await fetch(`${API_BASE}/clear_database`, {
        method: "POST",
    })

    return processResponse(response);
}