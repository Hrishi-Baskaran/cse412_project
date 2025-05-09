import React, { useEffect, useState } from 'react';
import axios from 'axios';

function OrganizationList() {
  const [organizations, setOrganizations] = useState([]);
  const [search, setSearch] = useState('');
  const [formData, setFormData] = useState({
    organization_name: '',
    profile: '',
    organization_card: ''
  });
  const [message, setMessage] = useState('');

  // get organizations from the backend
  const fetchOrganizations = () => {
    axios.get('http://127.0.0.1:5000/organization')
      .then(response => setOrganizations(response.data))
      .catch(error => console.error("Error fetching organizations:", error));
  };

  useEffect(() => { 
    fetchOrganizations();
  }, []);

  
  const handleInputChange = e => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  //create organization with post request
  const handleCreate = async () => {
    const form = new FormData();
    form.append('organization_name', formData.organization_name);
    form.append('profile', formData.profile);
    form.append('organization_card', formData.organization_card);
  
    try {
      const res = await axios.post('http://127.0.0.1:5000/organization', form);
      setMessage(res.data.message || 'Organization created successfully.');
    } catch (err) {
      if (err.response) {
        if (err.response.status === 409) {
          setMessage('❌ Organization already exists.');
        } else {
          setMessage(`❌ Error: ${err.response.data.error}`);
        }
      } else {
        setMessage('❌ Network error');
      }
    } finally {
      fetchOrganizations(); 
    }
  };
  
  //delete organization with delete request
  const handleDelete = async () => {
    const payload = {};
    if (formData.organization_name) payload.organization_name = formData.organization_name;
    if (formData.profile) payload.profile = formData.profile;
    if (formData.organization_card) payload.organization_card = formData.organization_card;
  
    try {
      const res = await axios.delete('http://127.0.0.1:5000/organization', {
        data: payload,
        headers: { 'Content-Type': 'application/json' }
      });
      setMessage(res.data?.message || 'Organization deleted successfully.');
    } catch (err) {
      console.error(err);
      setMessage('❌ Error deleting organization.');
    } finally {
      fetchOrganizations();
    }
  };
  
  //update organization with put request
  const handleUpdate = async () => {
    try {
      const res = await axios.put('http://127.0.0.1:5000/organization', {
        organization_name: formData.organization_name,
        profile: formData.profile || null,
        organization_card: formData.organization_card || null
      });
      setMessage(res.data.message || 'Update successful!');
      fetchOrganizations();
    } catch (err) {
      if (err.response && err.response.data?.error) {
        setMessage(`❌ Error: ${err.response.data.error}`);
      } else {
        setMessage('❌ Network error');
      }
    }
  };
  
  
  const filtered = organizations.filter(org =>
    org.organization_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ padding: '1rem', maxWidth: '700px' }}>
      <h2>🏢 Organization Manager</h2>

      <div style={{ marginBottom: '1rem' }}>
        <label>Organization Name:</label>
        <input
          name="organization_name"
          value={formData.organization_name}
          onChange={handleInputChange}
          placeholder="e.g., OpenAI"
          style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
        />

        <label>Profile:</label>
        <input
          name="profile"
          value={formData.profile}
          onChange={handleInputChange}
          placeholder="Short description"
          style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
        />

        <label>Organization Card:</label>
        <input
          name="organization_card"
          value={formData.organization_card}
          onChange={handleInputChange}
          placeholder="e.g., Leading AI Research Org"
          style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
        />

        <button onClick={handleCreate} style={{ marginRight: '1rem' }}>➕ Create</button>
        <button onClick={handleUpdate} style={{ marginRight: '1rem' }}>🔄 Update</button>
        <button onClick={handleDelete} style={{ color: 'red' }}>❌ Delete</button>

      </div>

      <input
        type="text"
        placeholder="🔍 Search organization..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{ marginBottom: '1rem', width: '100%' }}
      />

      {message && <p style={{ color: 'green' }}>{message}</p>}

      <ul>
        {filtered.map((org, index) => (
          <li key={index} style={{ marginBottom: '1rem' }}>
            <h3>{org.organization_name}</h3>
            <p><strong>Card:</strong> {org.organization_card}</p>
            <p><strong>Profile:</strong> {org.profile}</p>
          </li>
        ))}
        
      </ul>
    </div>
  );
}

export default OrganizationList;
