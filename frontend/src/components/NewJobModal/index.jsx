import { useEffect, useState } from "react";
import { Modal } from "antd";
import { Select, Space } from "antd";
import api from "../../api";

import "./styles.css";

export default function NewJobModal({ open, setOpen }) {
  const [workspaces, setWorkspaces] = useState([]);
  const [formJob, setFormJob] = useState({
    title: "",
    body: "",
    workspace_name: "",
  });

  const fetchWorkspaces = async () => {
    const workspaces = await api.jobs.getWorkspaces();
    console.log(workspaces);  
    setWorkspaces(workspaces);
  };

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  return (
    <>
      <Modal
        title="Create New Job"
        centered
        open={open}
        onCancel={() => setOpen(false)}
        width={1000}
      >
        <Space direction="vertical" id="container-new-job-modal">
          <input
            type="text"
            placeholder="Title"
            className="container-new-job-modal-item"
            value={formJob.title}
            style={{ width: "80%" }}
            onChange={(e) => setFormJob({ ...formJob, title: e.target.value })}
          />
          <Select
            options={workspaces}
            placeholder="Select a workspace"
            onChange={(value) =>
              setFormJob({ ...formJob, workspace_name: value })
            }
          />
          <textarea
            placeholder="Body"
            value={formJob.body}
            onChange={(e) => setFormJob({ ...formJob, body: e.target.value })}
          />
          <button onClick={() => console.log(formJob)}>Submit</button>
        </Space>
      </Modal>
    </>
  );
}
