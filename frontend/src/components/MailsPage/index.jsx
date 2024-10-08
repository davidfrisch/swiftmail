import { useEffect, useState } from "react";
import { Table, Button, message, Spin } from "antd";
import api from "../../api";
import "./MailsPage.css";
import JobStatus from "./JobStatus";

export default function MailsPage({ handleView }) {
  const [mails, setMails] = useState([]);
  const [fetchingNewMails, setFetchingNewMails] = useState(false);
  const [numMailNoJob, setNumMailNoJob] = useState(null);
  const [generatingJob, setGeneratingJob] = useState(null);
  const fetchNewMails = async () => {
    try {
      setFetchingNewMails(true);
      const mailsData = await api.enquiries.getNewEnquiries();
      setMails(mailsData);
      message.success("Fetched new mails successfully");
    } catch (error) {
      console.error("Failed to fetch mails:", error);
      message.error("Failed to fetch new mails");
    } finally {
      setFetchingNewMails(false);
    }
  };

  const fetchMails = async () => {
    try {
      const mailsData = await api.enquiries.getEnquiries();
      setMails(mailsData);
      const numNoJob = mailsData?.filter(({ job }) => !job).length || "N/A";
      setNumMailNoJob(numNoJob);
    } catch (error) {
      console.error("Failed to fetch mails:", error);
    }
  };

  useEffect(() => {
    fetchMails();
    const interval = setInterval(fetchMails, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleMarkAsRead = async (email) => {
    try {
      await api.enquiries.toggleAsRead(email.id);
      message.success(`Marked email with ID: ${email.id} as read`);
      setMails((mails) =>
        mails.map(({ mail, job }) =>
          mail.id === email.id
            ? { mail: { ...mail, is_read: !mail.is_read }, job }
            : { mail, job }
        )
      );
    } catch (error) {
      console.error("Failed to mark as read:", error);
      message.error("Failed to mark job as read");
    }
  };

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
      title: "Is Completed",
      dataIndex: "is_read",
      key: "isRead",
      width: 150,
      render: (isRead) => (isRead ? "Yes" : "No"),
    },
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
          <Button type="link" onClick={() => handleMarkAsRead(mail)}>
            {mail.is_read ? "Mark as Unread" : "Mark as Read"}
          </Button>
        </span>
      ),
      width: 200,
    },
  ];
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center" }}>
        <h1>Mails</h1>
        <h3 style={{ marginLeft: 20, paddingTop: 5 }}>
          (Number of Mails without Job: {numMailNoJob})
        </h3>
      </div>
      <div
        style={{ display: "flex", marginBottom: 16, justifyContent: "start" }}
      >
        {fetchingNewMails ? (
          <Spin />
        ) : (
          <Button type="primary" onClick={fetchNewMails}>
            Fetch New Mails
          </Button>
        )}
      </div>
      <Table
        columns={columns}
        dataSource={mails.map(({ mail, job }) => ({ ...mail, job }))}
        rowKey="id"
        pagination={{ pageSize: 5 }}
        className="mails-table"
      />
    </div>
  );
}
