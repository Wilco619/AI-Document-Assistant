import { NavLink, Outlet, Navigate, useLocation} from "react-router-dom"
import "./Users.css"


const AddUser = () => {
  const location = useLocation();
    
  if (location.pathname === '/home/users/Registration') {
    return <Navigate to="/home/users/Registration/AdminReg" />;
  }

  return (
    <div>
      <div className='regbtncontainer'>
        
          <NavLink className={"button"} to={"/home/users/Registration/AdminReg"}>+ New Admin</NavLink>
      </div>
      <div>
        <Outlet/>
      </div> 
    </div>
  )
}

export default AddUser