import { Button, Flex, Progress } from "antd";
import "./styles.css";
import { Typography } from "antd";

const { Title } = Typography;

const validation_titles = [
  "Quantitative Analysis",
  "Qualitative Analysis",
  "Similarity to previous conversations",
];

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
      <h2>Validation Scores</h2>
      <Flex justify="space-evenly">
        <div style={{ textAlign: "center" }}>
          <Progress percent={accuracy * 100} type="circle" size={"small"}/>
          <Title level={5}  style={{ margin: 0, height: "40px" }}>Accuracy</Title>
        </div>
        <div style={{ textAlign: "center" }}>
          <Progress percent={confidence * 100} type="circle" size={"small"} />
          <Title level={5}  style={{ margin: 0, height: "40px" }}>Confidence</Title>
        </div>
      </Flex>
      {scores.map((score, index) => (
        <div key={index} style={{ color: getColor(score) }}>
          <Flex justify="space-between" style={{ margin: 0, height: "40px" }}>
            <h3>{validation_titles[index]}</h3>
            <span>{score}%</span>
          </Flex>
          <Progress size={"small"} percent={score} showInfo={false} />
        </div>
      ))}
      <button className="validate-button">Evaluate Conversation</button>
    </div>
  );
};

export default ValidationWidget;
