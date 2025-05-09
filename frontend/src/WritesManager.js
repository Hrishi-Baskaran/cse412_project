import React, { useState } from 'react';
import axios from 'axios';

const WritesManager = () => {
  const [formData, setFormData] = useState({
    paper_id: '',
    model_id: ''
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const BASE_URL = 'http://127.0.0.1:5000/writes';

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setMessage('');
    setError('');
  };

  const createWrite = async () => {
    try {
      await axios.post(BASE_URL, {
        person_id: formData.person_id,
        paper_id: formData.paper_id
      });
      setMessage(`Write relation created! Person with ID: ${formData.person_id} now authors Paper with ID ${formData.paper_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create write relation.');
    }
  };

  const updateWrite = async () => {
    if (!formData.paper_id) {
      setError('paper_id is required to update.');
      return;
    }
    try {
      await axios.put(BASE_URL, {
        person_id: formData.person_id,
        paper_id: formData.paper_id
      });
      setMessage('Write relation updated successfully.');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update write relation.');
    }
  };

  const deleteWrite = async () => {
    if (!formData.paper_id) {
      setError('paper_id is required to delete.');
      return;
    }
    try {
      await axios.delete(BASE_URL, {
        data: { paper_id: formData.paper_id, person_id: formData.person_id }
      });
      setMessage('Write relation deleted successfully.');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete write relation.');
    }
  };

  return (
    <div style={{ padding: '1rem', maxWidth: '600px' }}>
      <h2>🛠️ Manage Write Relation</h2>
      <div><label> To Create: Input unique ID</label></div>
      <div><label> To Update: Input the ID of write relation to update/delete</label></div>

      <label>Paper ID *:</label>
      <input
        type="text"
        name="paper_id"
        value={formData.paper_id}
        onChange={handleChange}
        placeholder="Enter paper_id"
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <label>Paper ID *:</label>
      <input
        type="text"
        name="person_id"
        value={formData.person_id}
        onChange={handleChange}
        placeholder="Enter person_id"
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <div style={{ marginTop: '1rem' }}>
        <button onClick={createWrite} style={{ marginRight: '1rem' }}>➕ Create</button>
        <button onClick={updateWrite} style={{ marginRight: '1rem' }}>🔄 Update</button>
        <button onClick={deleteWrite} style={{ color: 'red' }}>❌ Delete</button>
      </div>

      {message && <p style={{ color: 'green', marginTop: '1rem' }}>{message}</p>}
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
    </div>
  );
};

export default WritesManager;
