import React, { useState } from 'react';
import axios from 'axios';

const PaperManager = () => {
  const [formData, setFormData] = useState({
    paper_id: '',
    title: '',
    abstract: '',
    publication_date: ''
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const BASE_URL = 'http://127.0.0.1:5000/paper';

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setMessage('');
    setError('');
  };

  const createPaper = async () => {
    try {
      await axios.post(BASE_URL, {
        paper_id: formData.paper_id,
        title: formData.title,
        abstract: formData.abstract,
        publication_date: formData.publication_date
      });
      setMessage(`Paper created! ID: ${formData.paper_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create paper.');
    }
  };

  const updatePaper = async () => {
    if (!formData.paper_id) {
      setError('paper_id is required to update.');
      return;
    }
    try {
      await axios.put(BASE_URL, {
        paper_id: formData.paper_id,
        title: formData.title,
        abstract: formData.abstract,
        publication_date: formData.publication_date
      });
      setMessage('Paper updated successfully.');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update paper.');
    }
  };

  const deletePaper = async () => {
    if (!formData.paper_id) {
      setError('paper_id is required to delete.');
      return;
    }
    try {
      await axios.delete(BASE_URL, {
        data: { paper_id: formData.paper_id },
      });
      setMessage('Paper deleted successfully.');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete paper.');
    }
  };

  return (
    <div style={{ padding: '1rem', maxWidth: '600px' }}>
      <h2>🛠️ Manage Paper</h2>
      <div><label> To Create: Input unique ID</label></div>
      <div><label> To Update: Input the ID of paper to update/delete</label></div>

      <label>Paper ID *:</label>
      <input
        type="text"
        name="paper_id"
        value={formData.paper_id}
        onChange={handleChange}
        placeholder="Enter paper_id"
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <label>Title</label>
      <input
        type="text"
        name="title"
        value={formData.title}
        onChange={handleChange}
        placeholder='title here'
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <label>Abstract</label>
      <input
        type="text"
        name="abstract"
        value={formData.abstract}
        onChange={handleChange}
        placeholder='a short summary of the paper'
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <label>Publication Date</label>
      <input
        type="text"
        name="publication_date"
        value={formData.publication_date}
        onChange={handleChange}
        placeholder='mm-dd-yyyy'
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <div style={{ marginTop: '1rem' }}>
        <button onClick={createPaper} style={{ marginRight: '1rem' }}>➕ Create</button>
        <button onClick={updatePaper} style={{ marginRight: '1rem' }}>🔄 Update</button>
        <button onClick={deletePaper} style={{ color: 'red' }}>❌ Delete</button>
      </div>

      {message && <p style={{ color: 'green', marginTop: '1rem' }}>{message}</p>}
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
    </div>
  );
};

export default PaperManager;
