import React from "react";
import { Button, theme } from "antd";
import { useNavigate } from "react-router-dom";

export default function OriginalEmail({ email }) {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const navigate = useNavigate();

  return (
    <div
      style={{
        background: colorBgContainer,
        padding: 24,
        borderRadius: borderRadiusLG,
      }}
    >
      <Button
        type="secondary"
        style={{ marginBottom: 24 }}
        onClick={() => navigate("/mails")}
      >
        Back
      </Button>
      <h1>Email</h1>

      <h2>Subject: {email?.subject}</h2>
      <div className="draft-body"> {email && email?.body}</div>
    </div>
  );
}
