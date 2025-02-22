import "./Subdiv.css";
import { useEffect, useState } from "react";
import { FirstRowDivContent } from "../Data";
import api from "../../api";

const SubDiv = () => {
  const [customerCount, setCustomerCount] = useState(0);

  useEffect(() => {
    // Make the API call using the pre-configured axios instance
    api.get('/customer-count/')
      .then(response => {
        setCustomerCount(response.data.customer_count);
      })
      .catch(error => {
        console.error('Error fetching customer count:', error);
      });
  }, []);

  // Update the FirstRowDivContent dynamically with the customer count
  const updatedContent = FirstRowDivContent.map((item) => {
    if (item.text === "Customers") {
      return { ...item, Number: customerCount };
    }
    return item;
  });

  const formatNumberWithSeparator = (number) => {
    return number.toLocaleString();
  };

  return (
    <div className="sub-div-container">
      {updatedContent.map((item) => (
        <div className="sub-div" key={item.id}>
          <h1 className="title">{item.text}</h1>
          <p className="description">Total: {formatNumberWithSeparator(item.Number)}</p>
        </div>
      ))}
    </div>
  );
};

export default SubDiv;
