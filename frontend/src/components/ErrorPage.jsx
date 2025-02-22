import { Link } from "react-router-dom";
import "./ErrorPage.css";

const ErrorPage = () => {
  return (
    <div className="ErrorPage">
      <div id="error-page">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you are looking for doesn't exist or has been moved.</p>
        <Link to="/home" className="error-link">
          Return to Home
        </Link>
      </div>
    </div>
  );
};

export default ErrorPage;