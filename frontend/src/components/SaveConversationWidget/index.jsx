import { Input, Typography, Button } from "antd";
import "./styles.css";

const { TextArea } = Input;
const { Title, Text } = Typography;

const SaveConversationWidget = () => {
  return (
    <div className="save-conversation-widget">
      <Title  style={{ margin: "30px 0", height: "40px" }}level={3}>Save here what you want the system to remember for future conversations:</Title>
      <Text> Anonymisation of the conversation will be done automatically.</Text>
      <TextArea rows={10} />
      <div className="save-conversation-widget__button">
        <Button type="primary">Save</Button>
      </div>
    </div>
  );
};

export default SaveConversationWidget;
