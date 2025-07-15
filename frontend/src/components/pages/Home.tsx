import { React, useState } from 'react';
import PasswordRecovery from '../modals/PasswordRecovery';

const Home: React.FC = () => {
  const [showModal, setShowModal] = useState(false);

  return (
    <div>
      <h1>Главная страница</h1>
      <button
        style={{
          background: 'blue', color: 'white'
        }}
        onClick={() => { setShowModal(true) }}
      >
        Forgot password
      </button>
      <PasswordRecovery isVisible={showModal} onClose={() => setShowModal(false)} />
    </div>
  );
};

export default Home;
