import React, { useEffect, useState } from 'react';
import { styled, useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import MuiDrawer from '@mui/material/Drawer';
import MuiAppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import CssBaseline from '@mui/material/CssBaseline';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Tooltip from '@mui/material/Tooltip';
import Collapse from '@mui/material/Collapse';
import ExpandLess from '@mui/icons-material/ExpandLess';
import AccountMenu from '../components/sub-components/AccountMenu';
import { Outlet, Link, NavLink } from "react-router-dom";
import { ToastContainer } from 'react-toastify';
import { NavText } from './Data';
import "./App.css"
import api from "../api"
import { ACCESS_TOKEN } from '../constants';

const drawerWidth = 220;

const openedMixin = (theme) => ({
  width: drawerWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden',
});

const closedMixin = (theme) => ({
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden',
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up('sm')]: {
    width: `calc(${theme.spacing(8)} + 1px)`,
  },
});

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
    boxSizing: 'border-box',
    ...(open && {
      ...openedMixin(theme),
      '& .MuiDrawer-paper': openedMixin(theme),
    }),
    ...(!open && {
      ...closedMixin(theme),
      '& .MuiDrawer-paper': closedMixin(theme),
    }),
  }),
);

export default function MiniDrawer() {
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const [expandedItem, setExpandedItem] = useState(null);
  const [username, setUsername] = useState("");
  const [isLoggedIn, setLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkLoggedInUser = async () => {
      try {
        const token = localStorage.getItem(ACCESS_TOKEN);
        console.log("Access token:", token); // Debugging
        if (token) {
          const config = {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          };
          const response = await api.get("/api/user/", config);
          console.log("User data:", response.data); // Debugging
          setLoggedIn(true);
          setUsername(response.data.username);
        } else {
          setLoggedIn(false);
          setUsername("");
        }
      } catch (error) {
        console.error("Error fetching user data:", error); // Debugging
        setLoggedIn(false);
        setUsername("");
      } finally {
        setLoading(false);
      }
    };
    checkLoggedInUser();
  }, []);

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const handleExpandClick = (item) => {
    setExpandedItem(expandedItem === item ? null : item);
  };

  if (loading) {
    return <div>Loading...</div>; // Show loading state
  }

  return (
    <div>
      {isLoggedIn ? (
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />
          <AppBar position="fixed" open={open} sx={{ boxShadow:"none" }}>
            <Toolbar sx={{ backgroundColor: '#1f1f1f'}}>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                onClick={handleDrawerOpen}
                edge="start"
                sx={{
                  marginRight: 5,
                  ...(open && { display: 'none' }),
                }}
              >
                <MenuIcon />
              </IconButton>
              <IconButton
                color="inherit"
                aria-label="close drawer"
                onClick={handleDrawerClose}
                edge="start"
                sx={{
                  marginRight: 5,
                  ...(!open && { display: 'none' }),
                }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" component="div" sx={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', }}>
                <h2 className="welcome-text">Welcome back {username}.</h2>
                <AccountMenu />
              </Typography>
            </Toolbar>
          </AppBar>
          <Drawer variant="permanent" open={open}>
            <DrawerHeader>
              <p>logo here</p>
            </DrawerHeader>
            <Divider />
            <List>
              {NavText.map((item) => (
                <div key={item.id}>
                  <ListItem disablePadding sx={{ display: 'block' }}>
                    <Tooltip title={!open ? item.name : ''} placement="right">
                      <ListItemButton
                        onClick={() => handleExpandClick(item.id)}
                        sx={{
                          minHeight: 48,
                          justifyContent: open ? 'initial' : 'center',
                          px: 2.5,
                        }}
                      >
                        <ListItemIcon
                          sx={{
                            minWidth: 0,
                            mr: open ? 3 : 'auto',
                            justifyContent: 'center',
                          }}
                        >
                          {/* Replace with your icon logic */}
                          {item.icon || <MenuIcon />}
                        </ListItemIcon>
                        <ListItemText primary={item.name} sx={{ opacity: open ? 1 : 0 }} />
                        {open && (expandedItem === item.id ? <ExpandLess /> : <ChevronRightIcon />)}
                      </ListItemButton>
                    </Tooltip>
                  </ListItem>
                  <Collapse in={expandedItem === item.id && open} timeout="auto" unmountOnExit>
                    <List component="div" disablePadding>
                      {item.sublinks.map((subItem) => (
                        <ListItemButton 
                          component={Link} 
                          to={subItem.link} 
                          key={subItem.id} 
                          sx={{ pl: 4 }}
                        >
                          <ListItemText primary={subItem.name} />
                        </ListItemButton>
                      ))}
                    </List>
                  </Collapse>
                </div>
              ))}
            </List>
            <Divider />
          </Drawer>
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <DrawerHeader />
            <Outlet />
          </Box>
          <ToastContainer />
        </Box>
      ) : (
        <div className='warning-page'>
          <h2>Sorry!</h2>
          <h1>Please Login First</h1>
          <NavLink className={'button'} to="/">LogIn</NavLink>
        </div>
      )}
    </div>
  );
}


