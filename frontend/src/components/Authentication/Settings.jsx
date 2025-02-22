import React from 'react'
import { NavLink, Outlet } from "react-router-dom";

const Settings = () => {
  return (
    <div>
        <NavLink 
          className=""
          to="/home/settings/change-password"
        >
          Change Password
        </NavLink>
        <Outlet/>
    </div>
  )
}

export default Settings