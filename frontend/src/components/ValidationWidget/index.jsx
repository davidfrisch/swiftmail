import { Button, Flex, Progress } from "antd";
import "./styles.css";
import { Typography } from 'antd';

const { Title } = Typography;

const validation_titles = [
  "Quantitative Analysis",
  "Qualitative Analysis",
  "Similarity to previous conversations",
]

const ValidationWidget = () => {
  // Fake validation scores
  const scores = [80, 90, 70];
  const confidence = 0.8;
  const accuracy = 0.9;

  // Function to determine color based on score
  const getColor = (score) => {
    if (score >= 90) {
      return "green";
    } else if (score >= 80) {
      return "orange";
    } else {
      return "red";
    }
  };

  return (
    <div className="widget-container">
      <Title level={4}>Validation Scores</Title>
      <Flex justify="space-evenly">
        <div style={{ textAlign: "center" }}>
          <Title level={5}>Accuracy</Title>
          <Progress percent={accuracy * 100} type="circle" />
        </div>
        <div style={{ textAlign: "center" }}>
          <Title level={5}>Confidence</Title>
          <Progress percent={confidence * 100} type="circle" />
        </div>
      </Flex>
      {scores.map((score, index) => (
        <div key={index} style={{ color: getColor(score) }}>
          <Flex justify="space-between">
            <Title level={5}>{validation_titles[index]}</Title>
            <span>{score}%</span>
          </Flex>
          <Progress percent={score} showInfo={false} />
        </div>
      ))}
      <button className="validate-button">
        Evaluate Conversation
      </button>
     
    </div>
  );
};

export default ValidationWidget;
