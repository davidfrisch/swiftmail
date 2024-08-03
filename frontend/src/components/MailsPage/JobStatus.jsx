import React from "react";
import { Button, Tooltip, message } from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";

const colorsStatus = {
  FAILED: "#ff4d4f",
  PENDING: "#1890ff",
  COMPLETED: "#52c41a",
  EXTRACTING: "#faad14",
  ANSWERING: "#faad14",
  DRAFTING: "#faad14",
};

export default function JobStatus({ job, onCancel, onRestart }) {
  // Function to handle job actions
  const handleJobAction = (job) => {
    if (job.status !== "COMPLETED" && job.status !== "FAILED") {
      onCancel(job);
    } else if (job.status === "FAILED") {
      onRestart(job);
    }
  };

  if (!job) {
    return null;
  }

  return (
    <div
      key={job.id}
      style={{
        disabled: job.status === "COMPLETED",
        marginBottom: 8,
        padding: "4px 8px",
        borderRadius: "4px",
        backgroundColor: job.status === "FAILED" ? "#ffe6e6" : "#e6f7ff", // Different backgrounds for statuses
        color: colorsStatus[job.status],
      }}
      onClick={() => handleJobAction(job)}
    >
      {job.status}
    </div>
  );
}
