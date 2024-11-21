import React, { useEffect, useState } from "react";
import { Button, Input, message, Spin } from "antd";
import { CopyOutlined } from "@ant-design/icons";
import "./styles.css";
import JobStatus from "../EmailsPage/JobStatus";
const { TextArea } = Input;
import api from "../../api";

export default function GeneratorPage() {
  const [inputText, setInputText] = useState("");
  const [draftText, setDraftText] = useState("");
  const [email, setEmail] = useState(null);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setDraftText("");
    setLoading(true);
    const newEmailData = {
      subject: `Email create at ${new Date().toISOString()}`,
      body: inputText,
      workspace_name: "demo",
      additional_information: "",
    };
    try {
      const newEmail = await api.emails.createEmail(newEmailData);

      const responseJob = await api.jobs.createJob(newEmail.id);

      setJob(responseJob.job);
      setEmail(newEmail);
    } catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  const handleCopyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    message.success("Copied to clipboard!");
  };

  useEffect(() => {
    if (job) {
      const interval = setInterval(async () => {
        const jobStatusResponse = await api.jobs.getJob(job.id);
        const jobStatus = jobStatusResponse.job;
        if (jobStatus.status === "COMPLETED") {
          const results = await api.results.getResults(job.id);
          setDraftText(results.draft_result.body);
          setLoading(false);
          clearInterval(interval);
        } else if (jobStatus.status === "FAILED") {
          setLoading(false);
          clearInterval(interval);
        } else {
          setJob(jobStatus);
        }
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [job]);

  return (
    <div className="container">
      <div className="container-header">
        {loading ? (
          <Spin style={{ margin: "10px" }} />
        ) : (
          <Button
            type={`${draftText?.length ? "primary" : "default"}`}
            onClick={() => handleCopyToClipboard(draftText)}
            id="copy-to-clipboard"
            disabled={!draftText?.length}
          >
            <CopyOutlined />
          </Button>
        )}
      </div>
      <div className="textarea-container">
        <div className="input-box">
          <TextArea
            className="textarea"
            placeholder="Enter email text here..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            style={{ minHeight: "70vh" }}
          />
        </div>
        <div className="output-box">
          <TextArea
            className="textarea"
            placeholder="Draft email will appear here..."
            value={draftText}
            style={{ minHeight: "70vh" }}
            readOnly
          />
        </div>
      </div>
      {loading ? (
        <div className="job-status">
          <JobStatus job={job} />
        </div>
      ) : (
        <Button className="button-generate" onClick={handleGenerate}>
          Generate
        </Button>
      )}
    </div>
  );
}
