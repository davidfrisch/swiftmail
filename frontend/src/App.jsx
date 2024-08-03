import { useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";
import "./App.css";
import BreadcrumbComponent from "./components/BreadcrumbComponent";
import MailsPage from "./components/MailsPage";
import ResultsPage from "./components/ResultsPage";
import { Layout } from "antd";
import api from "./api";
const { Content, Footer } = Layout;

function App() {
  const [currentMail, setCurrentMail] = useState(null);
  const navigate = useNavigate();

  const handleView = (mail) => {
    setCurrentMail(mail);
    navigate(`/mails/${mail.id}`);
  };

  const handleBack = () => {
    setCurrentMail(null);
    navigate("/mails");
  };

  const handleGetMail = async (mailId) => {
    const email = await api.enquiries.getEnquiry(mailId);
    setCurrentMail(email);
  };

  useEffect(() => {
    const currentPath = window.location.pathname;
    if (currentPath === "/" || currentPath === "/mails") {
      navigate("/mails");
      setCurrentMail(null);
    }

    if (currentPath.includes("/mails/")) {
      const mailId = currentPath.split("/mails/")[1];
      handleGetMail(mailId);
    }
  }, [currentMail, navigate]);

  return (
    <Layout id="page-container">
      <header id="header">
        <BreadcrumbComponent mailId={currentMail?.id} handleBack={handleBack} />
      </header>
      <Content id="content-wrap">
        <Routes>
          <Route path="/" element={<MailsPage handleView={handleView} />} />
          <Route
            path="/mails"
            element={<MailsPage handleView={handleView} />}
          />
          {currentMail && (
            <Route
              path="/mails/:jobId"
              element={<ResultsPage jobId={currentMail?.job?.id} />}
            />
          )}
        </Routes>
      </Content>
      <Footer id="footer">Swiftmail ©{new Date().getFullYear()}</Footer>
    </Layout>
  );
}

function AppWithRouter() {
  return (
    <Router>
      <App />
    </Router>
  );
}

export default AppWithRouter;
