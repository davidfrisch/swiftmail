import React from "react";
import { Button, Progress, Tooltip, message } from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";

const colorsStatus = {
  FAILED: "#ff4d4f",
  PENDING: "#1890ff",
  COMPLETED: "#52c41a",
  EXTRACTING: "#faad14",
  ANSWERING: "#faad14",
  DRAFTING: "#faad14",
};

const progressStatus = {
  FAILED: { status: "exception", percent: 100 },
  PENDING: { status: "active", percent: 0 },
  EXTRACTING: { status: "active", percent: 25 },
  ANSWERING: { status: "active", percent: 50 },
  DRAFTING: { status: "active", percent: 50 },
  COMPLETED: { status: "success", percent: 100 },
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
        display: "flex",
        backgroundColor: job.status === "FAILED" ? "#ffe6e6" : "#e6f7ff", // Different backgrounds for statuses
        color: colorsStatus[job.status],
      }}
      onClick={() => handleJobAction(job)}
    >
      {job.status}
      <Progress percent={progressStatus[job.status].percent} status={progressStatus[job.status].status} style={{ flex: 1, margin: "0 8px" }} />
    </div>
  );
}
