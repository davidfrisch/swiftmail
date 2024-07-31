import { useState } from "react";
import "./App.css";
import BreadcrumbComponent from "./components/BreadcrumbComponent";
import MailsPage from "./components/MailsPage";
import ResultsPage from "./components/ResultsPage";
import { Layout } from "antd";
const { Header, Content, Footer } = Layout;

function App() {
  const [currentJob, setCurrentJob] = useState(null);

  const handleView = (job) => {
    setCurrentJob(job.id);
  };

  const handleBack = () => {
    setCurrentJob(null);
  }

  return (
    <>
      <Layout>
        <Header style={{ display: "flex", alignItems: "center" }}>
          <div className="demo-logo" />
        </Header>
        <Content style={{ padding: "0 64px" }}>
          <BreadcrumbComponent jobId={currentJob} handleBack={handleBack} />
          {currentJob ? (
            <ResultsPage jobId={currentJob} />
          ) : (
            <MailsPage handleView={handleView} />
          )}
        </Content>
        <Footer style={{ textAlign: "center" }}>
          Swiftmail ©{new Date().getFullYear()}
        </Footer>
      </Layout>
    </>
  );
}

export default App;
