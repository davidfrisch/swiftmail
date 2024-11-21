import { useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";
import "./App.css";
import BreadcrumbComponent from "./components/BreadcrumbComponent";
import EmailsPage from "./components/EmailsPage";
import ResultsPage from "./components/ResultsPage";
import { Layout } from "antd";
import api from "./api";
import GeneratorPage from "./components/GeneratorPage";
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
    const email = await api.emails.getEmail(mailId);
    setCurrentMail(email);
  };

  useEffect(() => {
    const currentPath = window.location.pathname;
    if (currentPath === "/" || currentPath === "/mails") {
      navigate("/");
      setCurrentMail(null);
    }

    if (currentPath.includes("/mails/")) {
      const mailId = currentPath.split("/mails/")[1];
      if (!isNaN(mailId)) {
        handleGetMail(mailId);
      } else {
        navigate("/");
        setCurrentMail(null);
      }
    }
  }, [navigate]);

  return (
    <Layout id="page-container">
      <header id="header">
        <BreadcrumbComponent mailId={currentMail?.id} handleBack={handleBack} />
      </header>
      <Content id="content-wrap">
        <Routes>
          <Route path="/" element={<GeneratorPage />} />
          <Route
            path="/mails"
            element={<EmailsPage handleView={handleView} />}
          />
          {currentMail && (
            <Route
              path="/mails/:jobId"
              element={<ResultsPage jobId={currentMail?.job?.id} />}
            />
          )}
        </Routes>
      </Content>
      <Footer id="footer">SwiftMail ©{new Date().getFullYear()}</Footer>
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
