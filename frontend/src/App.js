import React from 'react';
import OrganizationList from './OrganizationList';
import UserSummary from './UserSummary';
import PersonManager from './PersonManager';
import PaperManager from './PaperManager';
import WritesManager from './WritesManager';

function App() {
  return (
    <div className="App">
      <h1>Welcome to HuggingFaceDB</h1>
      <OrganizationList />
      <PersonManager />
      <PaperManager />
      <WritesManager/>
      <UserSummary />
    </div>
  );
}

export default App;
