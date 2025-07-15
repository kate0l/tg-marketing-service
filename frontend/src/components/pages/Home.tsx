import { useState } from 'react';
//-->
import PasswordRecovery from '../modals/PasswordRecovery';
//<--

const Home: React.FC = () => {
  //-->
  const [showModal, setShowModal] = useState(false);

  const openModal = () => {
    setShowModal(true);
  }

  const closeModal = () => {
    setShowModal(false);
  }
  //<--

  return (
    <div>
      <h1>Главная страница</h1>

      {/* --> */}
      <button
        style={{
          background: 'blue', color: 'white'
        }}
        onClick={openModal}
      >
        Forgot password
      </button>
      <PasswordRecovery isVisible={showModal} onClose={closeModal} />
      {/* <-- */}

    </div>
  );
};

export default Home;
