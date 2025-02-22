// CsvExport.jsx
import React ,{useState}from 'react';
import { CSVLink } from 'react-csv';


const CsvExport = ({ data, filename }) => {
    const [isHovered, setIsHovered] = useState(false);

    const baseStyle = {
        width: '100%',
        color: 'black',           // Text color
        textDecoration: 'none',   // Remove underline
        // backgroundColor: isHovered ? '#135D66' : '#0056b3', // Button background color
        padding: '8px 16px',      // Button padding
        borderRadius: '4px',      // Button border radius
        display: 'inline-block',  // Ensure button-like appearance
        transition: 'background-color 0.3s', // Smooth transition
    };

  return (
    
    <CSVLink
    data={data}
    filename={filename}
    style={baseStyle}
    onMouseEnter={() => setIsHovered(true)}
    onMouseLeave={() => setIsHovered(false)}
    target="_blank"
    >
    Export CSV</CSVLink>
      
   
  );
};

export default CsvExport;
