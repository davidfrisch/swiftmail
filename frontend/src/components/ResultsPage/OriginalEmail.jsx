import React from "react";
import { theme } from "antd";

export default function OriginalEmail({ email }) {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  return (
    <div
      style={{
        background: colorBgContainer,
        padding: 24,
        borderRadius: borderRadiusLG,
      }}
    >
      <h1>Email</h1>

      <h2>Subject: {email?.subject}</h2>
      <div className="draft-body"> {email && email?.body}</div>
    </div>
  );
}
