import { Breadcrumb } from "antd";

const BreadcrumbComponent = ({jobId, handleBack}) => {
  return (
    <Breadcrumb style={{ margin: "16px 0" }}>
      <Breadcrumb.Item> {jobId ? <a onClick={handleBack}>Emails</a> : "Emails"}</Breadcrumb.Item>
      {jobId && <Breadcrumb.Item>mail {jobId}</Breadcrumb.Item>}
    </Breadcrumb>
  );
};

export default BreadcrumbComponent;
