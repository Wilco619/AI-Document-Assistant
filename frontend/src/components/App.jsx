import { ToastContainer } from 'react-toastify';
import MiniDrawer from "./MainPage";

const App = ({ username }) => {
  return (
    <div>
      <MiniDrawer username={username} />
      <ToastContainer />
    </div>
  );
};

export default App;