import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import PeopleIcon from '@mui/icons-material/People';
import { FaBalanceScale } from "react-icons/fa";

export const FirstRowDivContent = [
  
]

export const NavText = [
  {
    id: 1,
    name: "Dashboard",
    icon: <DashboardOutlinedIcon />,
    sublinks: [
      { id: 1, name: "Dashboard", link: "/home/dashboard" },  // Add the link property
      { id: 2, name: "D-Items", link: "/home/dashboard/items" }, // Add the link property
    ],
  },
  {
    id: 2,
    name: "upload",
    icon: <PeopleIcon/>,
    sublinks: [
      { id: 1, name: "Upload Documents", link: "/home/upload/DocumentUpload" },  // Add the link property

      
    ],
  },
  {
    id: 3,
    name: "Users",
    icon: <PeopleIcon/>,
    sublinks: [
      { id: 1, name: "User Registration", link: "/home/users/Registration" },  // Add the link property
       // Add the link property
      
    ],
  },
];

