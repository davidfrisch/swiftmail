import React, { useEffect, useState } from "react";
import { Table, Button, message, Spin } from "antd";
import api from "../../api";
import "./MailsPage.css"; // Import the CSS file for custom styles

export default function MailsPage({ handleView }) {
  const [mails, setMails] = useState([]);
  const [fetchingNewMails, setFetchingNewMails] = useState(false);
  const fetchNewMails = async () => {
    try {
      setFetchingNewMails(true);
      const mailsData = await api.enquiries.getNewEnquiries();
      setMails(mailsData);
      message.success("Fetched new mails successfully");
    } catch (error) {
      console.error("Failed to fetch mails:", error);
    } finally {
      setFetchingNewMails(false);
    }
  };

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

  const handleMarkAsRead = async (email) => {
    try {
      await api.enquiries.toggleAsRead(email.id);
      message.success(`Marked email with ID: ${email.id} as read`);
      setMails((mails) =>
        mails.map((mail) =>
          mail.id === email.id ? { ...mail, is_read: !mail.is_read } : mail
        )
      );
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
      render: (_, mail) => (
        <span>
          <Button
            type="link"
            onClick={() => handleView(mail)}
            style={{ marginRight: 8 }}
          >
            View
          </Button>
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
      <h1>Mails</h1>
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
        dataSource={mails}
        rowKey="id"
        pagination={{ pageSize: 5 }} // Disable pagination if you want to show all rows
        className="mails-table" // Add a custom class for styling
      />
    </div>
  );
}
