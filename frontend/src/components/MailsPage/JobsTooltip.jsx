import React from "react";
import { Button, Tooltip, message } from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";

const colorsStatus = {
  FAILED: "#ff4d4f",
  COMPLETED: "#52c41a",
  EXTRACTING: "#faad14",
  ANSWERING: "#faad14",
  DRAFTING: "#faad14",
};

export default function JobsTooltip({ jobs, onCancel, onRestart }) {
  // Function to handle job actions
  const handleJobAction = (job) => {
    console.log(job.status);
    if (job.status !== "COMPLETED" && job.status !== "FAILED") {
      onCancel(job);
    } else if (job.status === "FAILED") {
      onRestart(job);
    } 
  };

  // Create a tooltip content with clickable job statuses
  const tooltipContent = (
    <div
      style={{
        width: 210,
        backgroundColor: "#fff", // Light background for tooltip
        padding: "8px 12px",
        borderRadius: "4px",
        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.15)", // Subtle shadow for depth
      }}
    >
      {jobs.map((job) => (
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
          <strong>Job</strong> {job.id}: - <strong>Status:</strong>{" "}
          {job.status} 
          
        </div>
      ))}
    </div>
  );

  return (
    <Tooltip title={tooltipContent} placement="right">
      <InfoCircleOutlined style={{ fontSize: 24, cursor: "pointer" }} />
    </Tooltip>
  );
}
