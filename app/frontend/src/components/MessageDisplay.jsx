export default function MessageDisplay({message, error}) {
    if(!message && ! error) return null;

    return(
        <div style={{ marginTop: "1rem" }}>
            {message && (
                <pre
                    style={{
                        background: "#f4f4f4",
                        padding: "1rem",
                        whiteSpace: "pre-wrap",
                    }}
                >
                    {message}
                </pre>
            )}
            {error&& (
                <div style={{ color: "red", marginTop: "0.5rem"}}>
                    {error}
                </div>
            )}
        </div>
    );
}