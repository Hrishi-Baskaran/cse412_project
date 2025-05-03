import React, { useState } from 'react';
import axios from 'axios';

function UserDashboard() {
  const [username, setUsername] = useState('');
  const [person, setPerson] = useState(null);
  const [writes, setWrites] = useState([]);
  const [creates, setCreates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [allPapers, setAllPapers] = useState([]);
  const [allDatasets, setAllDatasets] = useState([]);
  const [allModels, setAllModels] = useState([]);
  
// Fetch all paper information, models and datasets
  const getPaperDetails = (paper_id) => {
    return allPapers.find(paper => paper.paper_id === paper_id) || {};
 };
 const getRepoDetails = (repo_id) => {
    return (
      allModels.find(model => model.repo_id === repo_id) ||
      allDatasets.find(dataset => dataset.repo_id === repo_id)
    );
  };
  const fetchUserData = async () => {
    setLoading(true);
    setError('');
    setPerson(null);
    setWrites([]);
    setCreates([]);
    setAllPapers([]);
    try {
      //Get person by username
      const personRes = await axios.get(`http://127.0.0.1:5000/person?huggingface_username=${username}`);
      const user = personRes.data[0];

      if (!user) {
        setError('User not found.');
        setLoading(false);
        return;
      }

      setPerson(user);

      //Get writes papers
      const writesRes = await axios.get(`http://127.0.0.1:5000/writes?person_id=${user.person_id}`);
      setWrites(writesRes.data);

      //Get creates models and datasets
      const models = await axios.get(`http://127.0.0.1:5000/creates?type=model&person_id=${user.person_id}`);
      const datasets = await axios.get(`http://127.0.0.1:5000/creates?type=dataset&person_id=${user.person_id}`);
      const papersRes = await axios.get('http://127.0.0.1:5000/paper');
      setAllPapers(papersRes.data);
      setCreates([...models.data, ...datasets.data]);

      const modelsRes = await axios.get('http://127.0.0.1:5000/model');
      const datasetsRes = await axios.get('http://127.0.0.1:5000/dataset');

      setAllModels(modelsRes.data);
      setAllDatasets(datasetsRes.data);
    } catch (err) {
      console.error(err);
      setError('Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>User Summary Dashboard</h2>

      <div style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Enter HuggingFace username..."
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ padding: '0.5rem', marginRight: '1rem' }}
        />
        <button onClick={fetchUserData}>Search</button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {person && (
        <div style={{ marginTop: '2rem' }}>
          <h3>👤 Person Info</h3>
          <p><strong>ID:</strong> {person.person_id}</p>
          <p><strong>HuggingFace Username:</strong> {person.huggingface_username}</p>
          <p><strong>Description: </strong>{person.person_description}</p>
          <p><strong>GitHub Link:</strong> <a href={person.github_link} target="_blank" rel="noreferrer">{person.github_link}</a></p>

          <h3>📝 Papers Written</h3>
            {writes.length === 0 ? (
            <p>No papers found.</p>
            ) : (
            <ul>
                {writes.map((w, i) => {
                const paper = getPaperDetails(w.paper_id);
                return (
                    <li key={i} style={{ marginBottom: '1rem' }}>
                    {paper ? (
                        <>
                        <strong>{paper.title}</strong><br />
                        <em>{paper.abstract}</em><br />
                        <small>Published: {paper.publication_date}</small>
                        </>
                    ) : (
                        <>Paper ID: {w.paper_id} (not found)</>
                    )}
                    </li>
                );
                })}
            </ul>
            )}

          <h3>⚙️ Created Repos</h3>
          {creates.length === 0 ? (
            <p>No models or datasets created.</p>
          ) : (
            <ul>
              {creates.map((c, i) => {
                const repo = getRepoDetails(c.repo_id);
                return (
                    <li key={i} style={{ marginBottom: '1rem' }}>
                    {repo ? (
                        <>
                        <strong>{repo.model_name || repo.dataset_name}</strong><br />
                        <em>{repo.description}</em><br />
                        </>
                    ) : (
                        <>Repo ID: {c.repo_id} (not found)</>
                    )}
                    </li>
                );
                })}

            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default UserDashboard;
