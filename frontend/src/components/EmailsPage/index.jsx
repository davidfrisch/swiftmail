import { useEffect, useState } from "react";
import { Table, Button, message, Spin } from "antd";
import api from "../../api";
import "./EmailsPage.css";
import JobStatus from "./JobStatus";
import NewJobModal from "../NewJobModal";

export default function EmailsPage({ handleView }) {
  const [emails, setEmails] = useState([]);
  const [isCreatingJob, setIsCreatingJob] = useState(false);
  const [generatingJob, setGeneratingJob] = useState(null);


  const fetchMails = async () => {
    try {
      const mailsData = await api.emails.getEmails();
      console.log(mailsData);
      setEmails(mailsData);
    } catch (error) {
      console.error("Failed to fetch mails:", error);
    }
  };

  useEffect(() => {
    fetchMails();
    const interval = setInterval(fetchMails, 5000);
    return () => clearInterval(interval);
  }, []);


  const handleGenerate = async (email) => {
    try {
      setGeneratingJob(email.id);
      await api.jobs.createJob(email.id);
      message.success(`Generated job for email with ID: ${email.id}`);
      fetchMails();
    } catch (error) {
      console.error("Failed to generate job:", error);
      message.error("Failed to generate job");
    } finally {
      setGeneratingJob(null);
    }
  };

  const handleRetryGenerate = async (email) => {
    try {
      setGeneratingJob(email.id);
      await api.jobs.retryJob(email.id);
      message.success(`Retrying generation for email with ID: ${email.id}`);
      fetchMails();
    } catch (error) {
      console.error("Failed to retry generating job:", error);
      message.error("Failed to retry generating job");
    } finally {
      setGeneratingJob(null);
    }
  }

  const renderActions = (mail) => {
    switch (mail?.job?.status) {
      case "COMPLETED":
        return (
          <Button
            type="link"
            onClick={() => handleView(mail)}
            style={{ marginRight: 8 }}
          >
            View
          </Button>
        );
      case "FAILED":
        return (
          <Button
            type="link"
            onClick={() => handleRetryGenerate(mail)}
            style={{ marginRight: 8 }}
          >
            Retry
          </Button>
        );
      default:
        return (
          <Button
            disabled
            type="link"
            style={{ marginRight: 8 }}
          >
            Generating
          </Button>
        );
    }
  };

  const columns = [
    {
      title: "Mail ID",
      dataIndex: "id",
      key: "id",
      width: 100,
    },
    {
      title: "Email Subject",
      dataIndex: "subject",
      key: "subject",
    },
    {
      title: "Status",
      dataIndex: "job",
      key: "job",
      render: (job) => <JobStatus job={job} />,
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, mail) => (
        <span>
          <div>
            {mail?.job ? (
              <div>
                {renderActions(mail)}
              </div>
            ) : (
              <Button
                type="link"
                disabled={
                  generatingJob ||
                  (mail?.job && mail?.job?.status !== "COMPLETED")
                }
                onClick={() => handleGenerate(mail)}
                style={{ marginRight: 8 }}
              >
                Generate
                {generatingJob && mail.id === generatingJob && <Spin />}
              </Button>
            )}
          </div>
        </span>
      ),
      width: 200,
    },
  ];
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center" }}>
        <h1>Mails</h1>
        
      </div>
      <div
        style={{ display: "flex", marginBottom: 16, justifyContent: "start" }}
      >
        {isCreatingJob ? (
          <NewJobModal open={isCreatingJob} setOpen={setIsCreatingJob} />
        ) : (
          <Button type="primary" onClick={() => setIsCreatingJob(true)}>
            Create New Job
          </Button>
        )}
      </div>
      <Table
        columns={columns}
        dataSource={emails.map(({email, job}) => ({ ...email, job }))}
        rowKey="id"
        pagination={{ pageSize: 5 }}
        className="mails-table"
      />
    </div>
  );
}
