import { useEffect, useState } from "react";
import { Modal } from "antd";
import { Select, Space,  Input, Form } from "antd";
import api from "../../api";

import "./styles.css";
const { TextArea } = Input;

export default function NewJobModal({ open, setOpen }) {
  const [workspaces, setWorkspaces] = useState([]);

  const [form] = Form.useForm();

  const fetchWorkspaces = async () => {
    const workspaces = await api.jobs.getWorkspaces();
    console.log(workspaces);
    setWorkspaces(workspaces);
  };

  const handleCreateJob = async () => {
    try {
      await form.validateFields();

      const newEmail = await api.emails.createEmail({
        "subject": form.getFieldValue("title") || `Email ${new Date().toISOString()}`,
        "workspace_name": form.getFieldValue("workspace_name"),
        "body": form.getFieldValue("body"),
        "additional_information": form.getFieldValue("additional_information"),
      });

      await api.jobs.createJob(newEmail.id);
      console.log("Job created successfully");

      setOpen(false);
    } catch (error) {
      console.error("Failed to create job:", error);
    }
  };

  const handleOnClose = () => {
    setOpen(false);
  };

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  return (
    <>
      <Form
        form={form}
        name="basic"
        initialValues={{ remember: true }}
        onFinish={handleCreateJob}
      >
        <Space direction="vertical" id="container-new-job-modal">
          <Modal
            title="Create New Job"
            centered
            open={open}
            onOk={handleCreateJob}
            onCancel={handleOnClose}
            width={1000}
          >
            <Form.Item name="title" rules={[{ required: false }]}>
              <Input
                type="text"
                placeholder="Title"
                className="container-new-job-modal-item"
                style={{ width: "80%" }}
              />
            </Form.Item>
            <Form.Item name="workspace_name" rules={[{ required: true }]}>
              <Select options={workspaces} placeholder="Select a workspace" />
            </Form.Item>
            <Form.Item name="body" rules={[{ required: true }]}>
              <TextArea
                placeholder="Email body"
                style={{ minHeight: 400, overflow: "auto" }}
              />
            </Form.Item>
            <Form.Item name="additional_information" rules={[{ required: true }]}>
              <TextArea
                placeholder="Add a note to help the generator"
                style={{ minHeight: 100, overflow: "auto" }}
              />
            </Form.Item>
          </Modal>
        </Space>
      </Form>
    </>
  );
}
