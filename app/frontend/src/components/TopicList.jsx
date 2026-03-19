export default function TopicList({ topics }) {
  return (
    <div>
      <h2>Topics in Database</h2>
      <ul>
        {topics.map((topic) => (
          <li key={topic}>{topic}</li>
        ))}
      </ul>
    </div>
  );
}