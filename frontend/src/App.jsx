import { useState } from "react";
import "./App.css";
import BreadcrumbComponent from "./components/BreadcrumbComponent";
import MailsPage from "./components/MailsPage";
import ResultsPage from "./components/ResultsPage";
import { Layout } from "antd";
const { Header, Content, Footer } = Layout;

function App() {
  const [currentMail, setCurrentMail] = useState(null);

  const handleView = (mail) => {
    setCurrentMail(mail);
  };

  const handleBack = () => {
    setCurrentMail(null);
  };

  return (
    <>
      <Layout>
        <Header style={{ display: "flex", alignItems: "center" }}>
          <div className="demo-logo" />
        </Header>
        <Content style={{ padding: "0 64px" }}>
          <BreadcrumbComponent jobId={currentMail?.job?.id} handleBack={handleBack} />
          {currentMail?.job?.id ? (
            <ResultsPage jobId={currentMail?.job?.id} />
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
