import React, { useState } from 'react';
import axios from 'axios';

const PersonManager = () => {
  const [formData, setFormData] = useState({
    person_id: '',
    huggingface_username: '',
    person_description: '',
    github_link: '',
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const BASE_URL = 'http://127.0.0.1:5000/person';

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setMessage('');
    setError('');
  };

  const createPerson = async () => {
    if (!formData.huggingface_username) {
      setError('Username is required to create a person.');
      return;
    }
    try {
      await axios.post(BASE_URL, {
        person_id: formData.person_id,
        huggingface_username: formData.huggingface_username,
        person_description: formData.person_description,
        github_link: formData.github_link,
      });
      setMessage(`Person created! ID: ${formData.person_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create person.');
    }
  };

  const updatePerson = async () => {
    if (!formData.person_id) {
      setError('person_id is required to update.');
      return;
    }
    try {
      await axios.put(BASE_URL, {
        person_id: formData.person_id,
        huggingface_username: formData.huggingface_username,
        person_description: formData.person_description,
        github_link: formData.github_link,
      });
      setMessage('Person updated successfully.');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update person.');
    }
  };

  const deletePerson = async () => {
    if (!formData.person_id) {
      setError('person_id is required to delete.');
      return;
    }
    try {
      await axios.delete(BASE_URL, {
        data: { person_id: formData.person_id },
      });
      setMessage('Person deleted successfully.');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete person.');
    }
  };

  return (
    <div style={{ padding: '1rem', maxWidth: '600px' }}>
      <h2>🛠️ Manage Person</h2>
      <div><label> To Create: Input unique ID and username</label></div>
      <div><label> To Update: Input the ID of person to update/delete</label></div>

      <label>Person ID *:</label>
      <input
        type="text"
        name="person_id"
        value={formData.person_id}
        onChange={handleChange}
        placeholder="Enter person_id"
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <label>HuggingFace Username *</label>
      <input
        type="text"
        name="huggingface_username"
        value={formData.huggingface_username}
        onChange={handleChange}
        placeholder="Required for create/update/delete"
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <label>Description</label>
      <input
        type="text"
        name="person_description"
        value={formData.person_description}
        onChange={handleChange}
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <label>GitHub Link</label>
      <input
        type="text"
        name="github_link"
        value={formData.github_link}
        onChange={handleChange}
        style={{ width: '100%', marginBottom: '0.5rem' }}
      />

      <div style={{ marginTop: '1rem' }}>
        <button onClick={createPerson} style={{ marginRight: '1rem' }}>➕ Create</button>
        <button onClick={updatePerson} style={{ marginRight: '1rem' }}>🔄 Update</button>
        <button onClick={deletePerson} style={{ color: 'red' }}>❌ Delete</button>
      </div>

      {message && <p style={{ color: 'green', marginTop: '1rem' }}>{message}</p>}
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
    </div>
  );
};

export default PersonManager;
