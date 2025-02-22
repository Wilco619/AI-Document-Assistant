// ExcelExport.jsx
import React ,{useState}from 'react';
import * as XLSX from 'xlsx';
import { Button } from '@mui/material';

const ExcelExport = ({ data, filename }) => {
  const handleExport = () => {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
    XLSX.writeFile(wb, filename);
  };

  const [isHovered, setIsHovered] = useState(false);

  const baseStyle = {
    width: '100%',
    color: 'black',                 // Text color
    // backgroundColor: isHovered ? '#135D66' : '#0056b3', // Background color with hover effect
    padding: '8px 14px',            // Button padding
    borderRadius: '4px',            // Button border radius
    display: 'inline-block',        // Ensure button-like appearance
    transition: 'background-color 0.3s', // Smooth transition
    textDecoration: 'none',         // Remove underline if applicable
  };

  return (
    <Button
      variant="contained"
      style={baseStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleExport}
    >
    Export Excel</Button>
  );
};

export default ExcelExport;
