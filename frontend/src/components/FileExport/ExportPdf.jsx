// PdfExport.jsx
import React from 'react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { Button } from '@mui/material';

const PdfExport = ({ data, filename }) => {
  const handleExport = () => {
    const doc = new jsPDF();
    const tableColumn = ['ID', 'First Name', 'Last Name', 'Age', 'Gender', 'Phone', 'Email', 'ID Number', 'Branch', 'Residence', 'Residence Type', 'Business Type', 'Business Area', 'Next of Keen', 'Guaranter Firstname', 'Guaranter Lastname', 'Guaranter Age', 'Guaranter Business Type', 'Guaranter Phone', 'Guaranter ID', 'Guaranter Gender', 'Created At', 'Updated At'];
    const tableRows = data.map(item => [
      item.id, item.firstname, item.lastname, item.age, item.gender, item.phone, item.email, item.id_number,
      item.branch, item.residence, item.residence_type, item.business_type, item.business_area, item.next_of_keen,
      item.guaranter_firstname, item.guaranter_lastname, item.guaranter_age, item.guaranter_business_type,
      item.guaranter_phone, item.guaranter_id, item.guaranter_gender, item.created_at, item.updated_at
    ]);

    doc.autoTable(tableColumn, tableRows);
    doc.save(filename);
  };

  return (
    <Button variant="contained" color="primary" onClick={handleExport}>
      Export to PDF
    </Button>
  );
};

export default PdfExport;
