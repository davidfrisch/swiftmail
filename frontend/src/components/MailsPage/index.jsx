import React, { useEffect, useState } from "react";
import { Table, Button, message } from "antd";
import api from "../../api";
import "./MailsPage.css"; // Import the CSS file for custom styles

export default function MailsPage({ handleView }) {
  const [mails, setMails] = useState([]);

  const fetchMails = async () => {
    try {
      const mailsData = await api.enquiries.getEnquiries();
      setMails(mailsData);
    } catch (error) {
      console.error("Failed to fetch mails:", error);
    }
  };

  useEffect(() => {
    fetchMails();
  }, []);

  const handleMarkAsRead = async (job) => {
    try {
      await api.mails.markAsRead(job.id);
      message.success(`Marked job with ID: ${job.id} as read`);
      // Update the job list to reflect the change if necessary
    } catch (error) {
      console.error("Failed to mark as read:", error);
      message.error("Failed to mark job as read");
    }
  };

  // Define columns for the Ant Design Table
  const columns = [
    {
      title: "Is Completed",
      dataIndex: "is_read",
      key: "isRead",
      width: 150,
      render: (isRead) => (isRead ? "Yes" : "No"),
    },
    {
      title: "Job ID",
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
      title: "Actions",
      key: "actions",
      render: (_, job) => (
        <span>
          <Button
            type="link"
            onClick={() => handleView(job)}
            style={{ marginRight: 8 }}
          >
            View
          </Button>
          <Button type="link" onClick={() => handleMarkAsRead(job)}>
            Mark as Read
          </Button>
        </span>
      ),
      width: 200,
    },
  ];
  return (
    <div>
      <h1>Mails</h1>
      <Table
        columns={columns}
        dataSource={mails}
        rowKey="id"
        pagination={false} // Disable pagination if you want to show all rows
        className="mails-table" // Add a custom class for styling
      />
    </div>
  );
}
