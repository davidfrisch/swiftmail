import { Breadcrumb } from "antd";

const BreadcrumbComponent = ({mailId, handleBack}) => {
  return (
    <Breadcrumb style={{ margin: "16px 0" }}>
      <Breadcrumb.Item> {mailId ? <a onClick={handleBack}>Emails</a> : "Emails"}</Breadcrumb.Item>
      {mailId && <Breadcrumb.Item>mail {mailId}</Breadcrumb.Item>}
    </Breadcrumb>
  );
};

export default BreadcrumbComponent;
