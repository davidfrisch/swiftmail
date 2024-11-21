import { Breadcrumb } from "antd";
import { Image } from "antd";

const BreadcrumbComponent = ({mailId, handleBack}) => {
  return (
    <Breadcrumb style={{ margin: "16px 0" }}>
      <Breadcrumb.Item> <Image src="src/assets/swift_mail_logo.png" width={70}/>SwiftMail {mailId ? <a onClick={handleBack}> - Emails</a> : ""}</Breadcrumb.Item>
      {mailId && <Breadcrumb.Item>mail {mailId}</Breadcrumb.Item>}
    </Breadcrumb>
  );
};

export default BreadcrumbComponent;
