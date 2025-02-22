
import 'react-toastify/dist/ReactToastify.css';
import "./Users.css"
import { Outlet } from 'react-router-dom';

const Users = () => {
  return (
    <div>
      <Outlet/>  
    </div>
  )
}

export default Users