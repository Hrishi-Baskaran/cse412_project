import React from 'react';
import OrganizationList from './OrganizationList';
import UserSummary from './UserSummary';
import PersonManager from './PersonManager';
function App() {
  return (
    <div className="App">
      <h1>Welcome to HuggingFaceDB</h1>
      <OrganizationList />
      <PersonManager />
      <UserSummary />
    </div>
  );
}

export default App;
